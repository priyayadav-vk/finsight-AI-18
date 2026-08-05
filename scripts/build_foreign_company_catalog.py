"""
Build a foreign (Top 500) company catalog by scraping S&P 500 constituents from Wikipedia
and validating tickers with Yahoo Finance (yfinance).

This script writes `data/foreign_live_companies.json` as a mapping of company name -> ticker.

Usage:
    .venv\Scripts\python.exe scripts\build_foreign_company_catalog.py

Notes:
- Requires `pandas` and `yfinance`.
- The script validates by calling `Ticker.history(period='2d')` and keeping tickers that returned data.
"""
import pandas as pd
import yfinance as yf
import time
import json
import os
import requests
from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / 'data'
DATA_DIR.mkdir(exist_ok=True)
OUT_FILE = DATA_DIR / 'foreign_live_companies.json'

WIKI_URL = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'

print('Fetching S&P 500 list from Wikipedia...')
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36'
}
try:
    resp = requests.get(WIKI_URL, headers=headers, timeout=30)
    resp.raise_for_status()
    html = resp.text
except Exception as e:
    print('Failed to fetch S&P 500 page:', e)
    raise SystemExit(1)

# Try to parse tables and pick the one that contains a 'Symbol' column
try:
    tables = pd.read_html(html)
    df = None
    for t in tables:
        cols = [c.lower() for c in t.columns.astype(str)]
        if 'symbol' in cols or 'ticker' in cols:
            df = t
            break
    if df is None:
        # Fallback: use BeautifulSoup to find the constituents table by id/class
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find('table', attrs={'id': 'constituents'}) or soup.find('table', class_='wikitable sortable')
        if table is None:
            raise ValueError('Could not find constituents table on the page')
        df = pd.read_html(str(table))[0]
    # Normalize expected columns
    col_map = {c: c for c in df.columns}
    # Ensure we have Symbol and Security/Company name columns
    possible_name_cols = [c for c in df.columns if 'security' in str(c).lower() or 'company' in str(c).lower() or 'name' in str(c).lower()]
    symbol_col = next((c for c in df.columns if 'symbol' in str(c).lower() or 'ticker' in str(c).lower()), None)
    name_col = possible_name_cols[0] if possible_name_cols else None
    if symbol_col is None or name_col is None:
        raise ValueError(f'Unexpected table columns: {list(df.columns)}')
    df = df[[symbol_col, name_col]].dropna()
    df.columns = ['Symbol', 'Security']
except Exception as e:
    print('Failed to parse S&P 500 table:', e)
    raise SystemExit(1)

candidates = list(df.itertuples(index=False, name=None))
print(f'Found {len(candidates)} candidates; validating via yfinance...')

validated = {}
count = 0
total = len(candidates)
for i, (symbol, name) in enumerate(candidates, start=1):
    symbol = str(symbol).strip()
    name = str(name).strip()
    try:
        t = yf.Ticker(symbol)
        data = t.history(period='2d')
        if data is not None and not data.empty:
            validated[name] = symbol
            count += 1
            print(f'[{i}/{total}] OK {symbol} -> {name} ({count})')
        else:
            print(f'[{i}/{total}] No data for {symbol} ({name})')
    except Exception as e:
        print(f'[{i}/{total}] Error validating {symbol}: {e}')
    # Throttle requests to avoid hitting remote limits
    time.sleep(0.15)
    # Periodically persist partial results
    if i % 50 == 0:
        try:
            with open(OUT_FILE, 'w', encoding='utf-8') as fh:
                json.dump(validated, fh, indent=2)
            print(f'Wrote partial results ({len(validated)} entries) to {OUT_FILE}')
        except Exception:
            pass

print(f'Validation complete. Keeping {len(validated)} tickers.')
try:
    with open(OUT_FILE, 'w', encoding='utf-8') as fh:
        json.dump(validated, fh, indent=2)
    print('Wrote', OUT_FILE)
except Exception as e:
    print('Failed to write output file:', e)
    raise SystemExit(1)
