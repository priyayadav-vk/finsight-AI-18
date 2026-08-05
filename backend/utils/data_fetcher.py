"""
Data Fetcher Module
Handles downloading live stock data from Yahoo Finance
Includes demo mode fallback for network issues
"""

import json
import time
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, timezone
import warnings
import io
from contextlib import redirect_stdout, redirect_stderr
import requests
warnings.filterwarnings('ignore')

import logging

from backend.config import AVAILABILITY_CACHE_TTL, ALL_INDIAN_COMPANIES, INDIAN_COMPANIES, HISTORICAL_DAYS, DATA_PATH, is_blocked_company_name
import os

logger = logging.getLogger(__name__)


class DataFetcher:
    """
    Fetches real-time and historical stock data from Yahoo Finance.
    
    Features:
    - Download historical data for training
    - Fetch live market data
    - Handle missing data gracefully
    - Cache data locally
    """
    
    def __init__(self):
        """Initialize the DataFetcher"""
        self.data_path = DATA_PATH
        os.makedirs(self.data_path, exist_ok=True)

    def _get_availability_cache_path(self):
        """Return the path to the Yahoo availability cache file."""
        return os.path.join(self.data_path, 'company_availability.json')

    def _load_availability_cache(self):
        """Load cached Yahoo availability metadata from local storage."""
        try:
            cache_file = self._get_availability_cache_path()
            if os.path.exists(cache_file):
                with open(cache_file, 'r', encoding='utf-8') as fh:
                    return json.load(fh)
        except Exception:
            pass
        return {}

    def _save_availability_cache(self, supported_companies, timestamp=None):
        """Save supported Yahoo company availability metadata locally."""
        try:
            cache_file = self._get_availability_cache_path()
            payload = {
                'timestamp': timestamp if timestamp is not None else time.time(),
                'supported_companies': supported_companies
            }
            with open(cache_file, 'w', encoding='utf-8') as fh:
                json.dump(payload, fh)
        except Exception:
            pass

    def _is_yahoo_service_available(self, test_ticker=None):
        """Return True if Yahoo Finance can be reached and returns data."""
        available, _ = self._probe_yahoo_status(test_ticker=test_ticker)
        return available

    def _probe_yahoo_status(self, test_ticker=None):
        """Probe Yahoo Finance service for availability and provide a status message."""
        candidates = []
        if test_ticker:
            candidates.append(test_ticker)
        candidates += ['RELIANCE.NS', 'INFY.NS', 'TCS.NS']

        last_exc = None
        import urllib.request as _urllib

        for cand in candidates:
            yahoo_ticker = self._resolve_ticker_for_yahoo(cand)
            attempts = 3
            delay = 1
            for attempt in range(1, attempts + 1):
                try:
                    with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                        stock = yf.Ticker(yahoo_ticker)
                        data = stock.history(period='2d')

                    if data is not None and not data.empty:
                        return True, f'Yahoo responded for test ticker {cand}'

                    # empty result - try a direct HTTP quote endpoint as fallback
                    try:
                        url = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={yahoo_ticker}"
                        req = _urllib.Request(url, headers={
                            'User-Agent': 'Mozilla/5.0 (compatible; FinSightAI/1.0)'
                        })
                        with _urllib.urlopen(req, timeout=10) as resp:
                            status = getattr(resp, 'status', None)
                            raw = resp.read()
                            try:
                                decoded = raw.decode('utf-8', errors='replace')
                            except Exception:
                                decoded = str(raw)

                            try:
                                parsed = json.loads(decoded)
                                results = parsed.get('quoteResponse', {}).get('result', [])
                                if results:
                                    logger.debug('Yahoo quote endpoint returned JSON for %s (status=%s)', cand, status)
                                    return True, f'Yahoo quote endpoint returned data for {cand}'
                                else:
                                    # No results in JSON response
                                    last_exc = Exception(f'Yahoo quote endpoint returned empty "result" for {cand} (status={status}) body_snippet={decoded[:2000]!r}')
                            except Exception as je:
                                # Non-JSON or decode error — capture body for diagnostics
                                last_exc = Exception(f'Non-JSON response for {cand} (status={status}) on attempt {attempt}: body_snippet={decoded[:2000]!r} json_error={str(je)}')
                                logger.debug('Non-JSON response for %s: %s', cand, decoded[:2000])
                    except Exception as http_e:
                        # Network/timeout/HTTP-level error
                        last_exc = http_e
                        logger.debug('HTTP probe error for %s: %s', cand, str(http_e))

                    if last_exc is None:
                        last_exc = Exception(f'Empty data for {cand} on attempt {attempt}')
                except Exception as e:
                    last_exc = e
                time.sleep(delay)
                delay = min(delay * 2, 8)

        msg = f"Yahoo returned no data for test tickers tried: {candidates}"
        if last_exc:
            msg += f"; last error: {str(last_exc)}"

        return False, msg

    def check_yahoo_status(self, test_ticker=None):
        """
        Quick check to verify Yahoo Finance service is responding.

        Uses a small set of reliable tickers and retries with exponential backoff to reduce false negatives.

        Returns a dict with keys: 'available' (bool), 'message' (str), 'last_checked' (ISO datetime)
        """
        available, message = self._probe_yahoo_status(test_ticker=test_ticker)
        return {
            'available': available,
            'message': message,
            'last_checked': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

    def yahoo_verbose_probe(self, tickers):
        """
        Run verbose HTTP diagnostics against Yahoo endpoints for the provided tickers.
        Returns a mapping ticker -> diagnostic dict with status codes, headers and small body snippets.
        """
        results = {}
        import requests
        for t in (tickers or []):
            sym = self._resolve_ticker_for_yahoo(t)
            diag = {'ticker': t, 'resolved': sym, 'steps': []}
            try:
                session = requests.Session()
                base_headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                }
                # 1) GET quote page
                quote_page = f'https://finance.yahoo.com/quote/{sym}'
                try:
                    r = session.get(quote_page, headers=base_headers, timeout=10)
                    diag['steps'].append({'step': 'quote_page_get', 'status_code': r.status_code, 'reason': r.reason, 'content_type': r.headers.get('Content-Type'), 'snippet': (r.text[:1000] if r.text else '')})
                except Exception as e:
                    diag['steps'].append({'step': 'quote_page_get', 'error': str(e)})

                # 2) Chart endpoint
                chart_url = f'https://query1.finance.yahoo.com/v8/finance/chart/{sym}?range=5d&interval=1d'
                headers = dict(base_headers)
                headers['Referer'] = quote_page
                headers['Accept'] = 'application/json, text/javascript, */*; q=0.01'
                try:
                    r2 = session.get(chart_url, headers=headers, timeout=10)
                    snippet = ''
                    try:
                        snippet = r2.text[:2000]
                    except Exception:
                        snippet = ''
                    diag['steps'].append({'step': 'chart_endpoint', 'status_code': r2.status_code, 'reason': r2.reason, 'content_type': r2.headers.get('Content-Type'), 'snippet': snippet})
                except Exception as e:
                    diag['steps'].append({'step': 'chart_endpoint', 'error': str(e)})

                # 3) Quote endpoint
                quote_url = f'https://query1.finance.yahoo.com/v7/finance/quote?symbols={sym}'
                try:
                    r3 = session.get(quote_url, headers=headers, timeout=10)
                    snippet = ''
                    try:
                        snippet = r3.text[:2000]
                    except Exception:
                        snippet = ''
                    diag['steps'].append({'step': 'quote_endpoint', 'status_code': r3.status_code, 'reason': r3.reason, 'content_type': r3.headers.get('Content-Type'), 'snippet': snippet})
                except Exception as e:
                    diag['steps'].append({'step': 'quote_endpoint', 'error': str(e)})

            except Exception as ex:
                diag['error'] = str(ex)
            results[t] = diag
        return results

    def _resolve_ticker_for_yahoo(self, ticker):
        """
        Normalize market symbols so Yahoo Finance can resolve them reliably.
        For Indian BSE codes such as 500002.BO, map them to the matching NSE
        ticker like 3MINDIA.NS when available.
        """
        normalized_ticker = str(ticker).strip()

        if normalized_ticker.endswith('.BO'):
            for company_name, tickers in INDIAN_COMPANIES.items():
                if tickers.get('BSE', '').upper() == normalized_ticker.upper():
                    nse_ticker = tickers.get('NSE')
                    if nse_ticker:
                        return nse_ticker

        return normalized_ticker
    
    def fetch_live_data(self, ticker):
        """
        Fetch the latest live data for a stock with multi-provider fallback.
        Tries (in order): Yahoo (yfinance), Alpha Vantage (if ALPHAVANTAGE_API_KEY set),
        TwelveData (if TWELVEDATA_API_KEY set). Falls back to demo data.
        """
        yahoo_ticker = self._resolve_ticker_for_yahoo(ticker)

        # helper to present IST times
        def _ist_now():
            return datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=5, minutes=30)))

        def _market_status_for(now):
            market_open = now.replace(hour=9, minute=15, second=0, microsecond=0)
            market_close = now.replace(hour=15, minute=30, second=0, microsecond=0)
            if now.weekday() < 5:
                if market_open <= now <= market_close:
                    return "[OPEN]"
                return "[CLOSED]"
            return "[CLOSED] (Weekend)"

        # Internal attempt: Alpha Vantage
        def _try_alpha_vantage(sym):
            key = os.environ.get('ALPHAVANTAGE_API_KEY')
            if not key:
                return None
            try:
                symbol = str(sym).split('.')[0]
                url = 'https://www.alphavantage.co/query'
                params = {'function': 'GLOBAL_QUOTE', 'symbol': symbol, 'apikey': key}
                resp = requests.get(url, params=params, timeout=10)
                if resp.status_code != 200:
                    logger.debug('AlphaVantage non-200: %s', resp.status_code)
                    return None
                payload = resp.json()
                gq = payload.get('Global Quote') or payload.get('Global Quote', {})
                if not gq:
                    return None
                price = gq.get('05. price') or gq.get('05.price')
                open_p = gq.get('02. open')
                high_p = gq.get('03. high')
                low_p = gq.get('04. low')
                prev_close = gq.get('08. previous close') or gq.get('08.previous close')
                vol = gq.get('06. volume')
                last_trade_date = gq.get('07. latest trading day')

                now = _ist_now()
                last_updated = now
                if last_trade_date:
                    try:
                        # Alpha returns date like YYYY-MM-DD
                        dt = datetime.fromisoformat(last_trade_date)
                        last_updated = dt.replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=5, minutes=30)))
                    except Exception:
                        last_updated = now

                return {
                    'ticker': ticker,
                    'company_name': ticker,
                    'current_price': float(price) if price is not None else 0.0,
                    'open_price': float(open_p) if open_p is not None else 0.0,
                    'high_price': float(high_p) if high_p is not None else 0.0,
                    'low_price': float(low_p) if low_p is not None else 0.0,
                    'previous_close': float(prev_close) if prev_close is not None else 0.0,
                    'volume': int(vol) if vol is not None else 0,
                    'market_status': _market_status_for(now),
                    'last_updated': last_updated.strftime('%Y-%m-%d %H:%M:%S %Z'),
                    'date': last_updated.strftime('%Y-%m-%d'),
                    'data_source': 'AlphaVantage',
                    'is_fallback': False,
                    'is_demo': False
                }
            except Exception as e:
                logger.debug('AlphaVantage fetch failed for %s: %s', sym, e)
                return None

        # Internal attempt: TwelveData
        def _try_twelvedata(sym):
            key = os.environ.get('TWELVEDATA_API_KEY')
            if not key:
                return None
            try:
                url = 'https://api.twelvedata.com/quote'
                params = {'symbol': sym, 'apikey': key}
                resp = requests.get(url, params=params, timeout=10)
                if resp.status_code != 200:
                    logger.debug('TwelveData non-200: %s', resp.status_code)
                    return None
                payload = resp.json()
                if 'status' in payload and payload.get('status') == 'error':
                    return None
                price = payload.get('price')
                open_p = payload.get('open')
                high_p = payload.get('high')
                low_p = payload.get('low')
                prev_close = payload.get('previous_close') or payload.get('previousClose')
                vol = payload.get('volume')
                dt = payload.get('datetime') or payload.get('timestamp')

                now = _ist_now()
                last_updated = now
                if dt:
                    try:
                        # TwelveData may return ISO datetime
                        last_updated = pd.to_datetime(dt).to_pydatetime()
                        if last_updated.tzinfo is None:
                            last_updated = last_updated.replace(tzinfo=timezone.utc)
                        last_updated = last_updated.astimezone(timezone(timedelta(hours=5, minutes=30)))
                    except Exception:
                        last_updated = now

                return {
                    'ticker': ticker,
                    'company_name': ticker,
                    'current_price': float(price) if price is not None else 0.0,
                    'open_price': float(open_p) if open_p is not None else 0.0,
                    'high_price': float(high_p) if high_p is not None else 0.0,
                    'low_price': float(low_p) if low_p is not None else 0.0,
                    'previous_close': float(prev_close) if prev_close is not None else 0.0,
                    'volume': int(vol) if vol is not None else 0,
                    'market_status': _market_status_for(now),
                    'last_updated': last_updated.strftime('%Y-%m-%d %H:%M:%S %Z'),
                    'date': last_updated.strftime('%Y-%m-%d'),
                    'data_source': 'TwelveData',
                    'is_fallback': False,
                    'is_demo': False
                }
            except Exception as e:
                logger.debug('TwelveData fetch failed for %s: %s', sym, e)
                return None

        # 1) Try Yahoo via yfinance (quietly)
        try:
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                stock = yf.Ticker(yahoo_ticker)
                data = stock.history(period='5d')

            if data is not None and not data.empty:
                latest = data.iloc[-1]
                info = stock.info if hasattr(stock, 'info') else {}

                # timestamp handling
                data_ts = None
                try:
                    data_index = latest.name
                    data_ts = pd.to_datetime(data_index)
                    if data_ts.tzinfo is None:
                        data_ts = data_ts.replace(tzinfo=timezone.utc)
                    data_ts_ist = data_ts.astimezone(timezone(timedelta(hours=5, minutes=30)))
                    last_updated_str = data_ts_ist.strftime("%Y-%m-%d %H:%M:%S %Z")
                    date_str = data_ts_ist.strftime("%Y-%m-%d")
                except Exception:
                    now = _ist_now()
                    last_updated_str = now.strftime('%Y-%m-%d %H:%M:%S %Z')
                    date_str = now.strftime('%Y-%m-%d')

                # Safely extract numeric fields
                def _safe_get(row, col, cast=float, default=0):
                    try:
                        val = row[col]
                        if pd.isna(val):
                            return default
                        return cast(val)
                    except Exception:
                        return default

                previous_close = _safe_get(latest, 'Close', float, 0.0)
                if len(data) > 1:
                    try:
                        previous_close = float(data.iloc[-2]['Close'])
                    except Exception:
                        pass

                live_data = {
                    'ticker': ticker,
                    'company_name': info.get('longName', ticker),
                    'current_price': _safe_get(latest, 'Close', float, 0.0),
                    'open_price': _safe_get(latest, 'Open', float, 0.0),
                    'high_price': _safe_get(latest, 'High', float, 0.0),
                    'low_price': _safe_get(latest, 'Low', float, 0.0),
                    'previous_close': float(previous_close),
                    'volume': int(_safe_get(latest, 'Volume', int, 0)),
                    'market_status': _market_status_for(_ist_now()),
                    'last_updated': last_updated_str,
                    'date': date_str,
                    'data_index_timestamp_utc': data_ts.isoformat() if data_ts is not None else None,
                    'data_source': 'Yahoo'
                }
                return live_data

        except Exception as e:
            logger.debug('Yahoo fetch failed for %s: %s', ticker, e)
            # If Yahoo via yfinance failed, attempt a direct HTTP session-based fetch that
            # obtains cookies and uses query/chart endpoints with Referer headers.

            def _try_yahoo_http_session(sym):
                try:
                    session = requests.Session()
                    base_headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36',
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                    }
                    quote_page = f'https://finance.yahoo.com/quote/{sym}'
                    # Initial GET to obtain cookies and any session tokens
                    r = session.get(quote_page, headers=base_headers, timeout=10)
                    if r.status_code not in (200, 201):
                        logger.debug('Yahoo direct page GET returned %s for %s', r.status_code, sym)
                    # Try chart endpoint which often returns structured JSON
                    chart_url = f'https://query1.finance.yahoo.com/v8/finance/chart/{sym}?range=5d&interval=1d'
                    h = dict(base_headers)
                    h['Referer'] = quote_page
                    h['Accept'] = 'application/json, text/javascript, */*; q=0.01'
                    r2 = session.get(chart_url, headers=h, timeout=10)
                    if r2.status_code == 200:
                        try:
                            payload = r2.json()
                            chart = payload.get('chart', {})
                            result = None
                            results = chart.get('result')
                            if isinstance(results, list) and len(results) > 0:
                                result = results[0]
                            if result:
                                meta = result.get('meta', {})
                                timestamp = result.get('timestamp') or []
                                indicators = result.get('indicators', {})
                                quote = indicators.get('quote', [])
                                if quote and isinstance(quote, list):
                                    q = quote[0]
                                    closes = q.get('close', [])
                                    opens = q.get('open', [])
                                    highs = q.get('high', [])
                                    lows = q.get('low', [])
                                    volumes = q.get('volume', [])
                                    if closes:
                                        # pick the last non-null value
                                        for i in range(len(closes)-1, -1, -1):
                                            c = closes[i]
                                            if c is not None:
                                                close_v = float(c)
                                                open_v = float(opens[i]) if i < len(opens) and opens[i] is not None else close_v
                                                high_v = float(highs[i]) if i < len(highs) and highs[i] is not None else close_v
                                                low_v = float(lows[i]) if i < len(lows) and lows[i] is not None else close_v
                                                vol_v = int(volumes[i]) if i < len(volumes) and volumes[i] is not None else 0
                                                # timestamp handling
                                                ts = None
                                                if timestamp and i < len(timestamp):
                                                    try:
                                                        ts = datetime.fromtimestamp(int(timestamp[i]), tz=timezone.utc)
                                                    except Exception:
                                                        ts = None
                                                now = _ist_now()
                                                if ts is not None:
                                                    last_updated = ts.astimezone(timezone(timedelta(hours=5, minutes=30)))
                                                else:
                                                    last_updated = now

                                                return {
                                                    'ticker': ticker,
                                                    'company_name': ticker,
                                                    'current_price': close_v,
                                                    'open_price': open_v,
                                                    'high_price': high_v,
                                                    'low_price': low_v,
                                                    'previous_close': close_v,
                                                    'volume': vol_v,
                                                    'market_status': _market_status_for(_ist_now()),
                                                    'last_updated': last_updated.strftime('%Y-%m-%d %H:%M:%S %Z'),
                                                    'date': last_updated.strftime('%Y-%m-%d'),
                                                    'data_source': 'Yahoo-Chart-Endpoint',
                                                    'is_fallback': False,
                                                    'is_demo': False
                                                }
                        except Exception as je:
                            logger.debug('Failed to parse Yahoo chart JSON for %s: %s', sym, je)
                    else:
                        logger.debug('Yahoo chart endpoint returned %s for %s', r2.status_code, sym)

                    # As a fallback, try the quote endpoint
                    quote_url = f'https://query1.finance.yahoo.com/v7/finance/quote?symbols={sym}'
                    r3 = session.get(quote_url, headers=h, timeout=10)
                    if r3.status_code == 200:
                        try:
                            payload = r3.json()
                            results = payload.get('quoteResponse', {}).get('result', [])
                            if results:
                                res = results[0]
                                price = res.get('regularMarketPrice') or res.get('regularMarketPreviousClose')
                                open_p = res.get('regularMarketOpen')
                                high_p = res.get('regularMarketDayHigh')
                                low_p = res.get('regularMarketDayLow')
                                prev = res.get('regularMarketPreviousClose')
                                vol = res.get('regularMarketVolume') or res.get('volume') or 0
                                now = _ist_now()
                                return {
                                    'ticker': ticker,
                                    'company_name': res.get('longName') or ticker,
                                    'current_price': float(price) if price is not None else 0.0,
                                    'open_price': float(open_p) if open_p is not None else 0.0,
                                    'high_price': float(high_p) if high_p is not None else 0.0,
                                    'low_price': float(low_p) if low_p is not None else 0.0,
                                    'previous_close': float(prev) if prev is not None else 0.0,
                                    'volume': int(vol),
                                    'market_status': _market_status_for(_ist_now()),
                                    'last_updated': now.strftime('%Y-%m-%d %H:%M:%S %Z'),
                                    'date': now.strftime('%Y-%m-%d'),
                                    'data_source': 'Yahoo-Quote-Endpoint',
                                    'is_fallback': False,
                                    'is_demo': False
                                }
                        except Exception as je:
                            logger.debug('Failed to parse Yahoo quote JSON for %s: %s', sym, je)
                    else:
                        logger.debug('Yahoo quote endpoint returned %s for %s', r3.status_code, sym)

                except Exception as ex:
                    logger.debug('Yahoo HTTP session attempt failed for %s: %s', sym, ex)
                return None

            # Try improved Yahoo HTTP session fetch
            yahoo_http_result = _try_yahoo_http_session(yahoo_ticker)
            if yahoo_http_result:
                return yahoo_http_result

        # 2) Try Alpha Vantage if API key provided
        alpha_result = _try_alpha_vantage(yahoo_ticker)
        if alpha_result:
            return alpha_result

        # 3) Try TwelveData if API key provided
        td_result = _try_twelvedata(yahoo_ticker)
        if td_result:
            return td_result

        # 4) As a last resort, return demo fallback
        logger.info('All live providers failed for %s; returning demo fallback', ticker)
        try:
            demo_data = self._get_demo_data(ticker, is_fallback=True)
            demo_data['data_source'] = 'Demo fallback after all providers failed'
            demo_data['is_fallback'] = True
            return demo_data
        except Exception as fallback_e:
            logger.exception('Demo fallback generation failed for %s: %s', ticker, fallback_e)
            return {
                'ticker': str(ticker),
                'company_name': str(ticker),
                'current_price': 0.0,
                'open_price': 0.0,
                'high_price': 0.0,
                'low_price': 0.0,
                'previous_close': 0.0,
                'volume': 0,
                'market_status': '[CLOSED] (Demo)',
                'last_updated': _ist_now().strftime('%Y-%m-%d %H:%M:%S %Z'),
                'date': _ist_now().strftime('%Y-%m-%d'),
                'is_demo': True,
                'is_fallback': True,
                'data_source': 'Hard fallback data'
            }
    
    def fetch_historical_data(self, ticker, days=HISTORICAL_DAYS):
        """
        Download historical data for machine learning training.
        
        Parameters:
        -----------
        ticker : str
            Stock ticker symbol
        days : int
            Number of historical days to fetch (default: 750 days ~3 years)
        
        Returns:
        --------
        pd.DataFrame : Historical OHLCV data
        """
        try:
            # Load cached historical data first to avoid repeated Yahoo requests
            cache_key = ticker.replace('.', '_')
            cached = self.load_cached_data(cache_key, cache_type='historical')
            if cached is not None and not cached.empty:
                return cached

            # Calculate start date
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            yahoo_ticker = self._resolve_ticker_for_yahoo(ticker)

            # Download data from Yahoo Finance
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                data = yf.download(
                    yahoo_ticker,
                    start=start_date,
                    end=end_date,
                    interval='1d',
                    progress=False,
                    auto_adjust=False,
                    actions=False
                )
            
            if data.empty:
                demo_data = self._generate_demo_historical_data(ticker)
                self.cache_data(cache_key, demo_data, cache_type='historical')
                return demo_data
            
            # Keep only the required OHLCV columns, regardless of Yahoo's extra columns
            required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            missing_columns = [col for col in required_columns if col not in data.columns]
            if missing_columns:
                raise ValueError(f"Missing required columns for {ticker}: {missing_columns}")
            
            data = data[required_columns].copy()
            
            # Reset index to make date a column
            data.reset_index(inplace=True)
            
            # Rename 'Date' column
            data.rename(columns={'Date': 'Date'}, inplace=True)
            
            # Remove rows with missing data
            data = data.dropna()
            
            # Ensure date column is datetime
            data['Date'] = pd.to_datetime(data['Date'])
            
            # Convert OHLCV columns to proper numeric types
            data['Open'] = pd.to_numeric(data['Open'], errors='coerce').astype(float)
            data['High'] = pd.to_numeric(data['High'], errors='coerce').astype(float)
            data['Low'] = pd.to_numeric(data['Low'], errors='coerce').astype(float)
            data['Close'] = pd.to_numeric(data['Close'], errors='coerce').astype(float)
            data['Volume'] = pd.to_numeric(data['Volume'], errors='coerce').astype(int)
            
            # Remove any rows with NaN after conversion
            data = data.dropna()

            self.cache_data(cache_key, data, cache_type='historical')
            
            return data
        
        except Exception as e:
            # Try demo mode as fallback
            demo_data = self._generate_demo_historical_data(ticker)
            self.cache_data(cache_key, demo_data, cache_type='historical')
            return demo_data
    
    def _get_demo_data(self, ticker, is_fallback=False):
        """
        Generate realistic demo market data for testing.
        This is a fallback when live Yahoo Finance data is unavailable.
        
        Parameters:
        -----------
        ticker : str
            Stock ticker symbol
        
        Returns:
        --------
        dict : Mock live market data
        """
        ticker = str(ticker or '').strip()

        # Look up company name from config
        company_name = None
        for name, tickers in INDIAN_COMPANIES.items():
            if tickers.get('NSE') == ticker or tickers.get('BSE') == ticker:
                company_name = name
                break
        
        if not company_name:
            company_name = ticker or 'Unknown Ticker'
        
        # Generate realistic stock prices (base price varies by company)
        base_prices = {
            'TCS': 3500, 'INFY': 1500, 'RELIANCE': 2500, 'HDFC': 2700,
            'ICICI': 950, 'SBIN': 550, 'MARUTI': 9000, 'BAJAJ': 8500,
            'WIPRO': 400, 'HCL': 1800
        }
        
        # Find a base price for this ticker
        base_price = base_prices.get(ticker.split('.')[0], 2000)
        
        # Add realistic random variation
        seed_value = hash(ticker) % (2**32)
        np.random.seed(seed_value)
        variation = np.random.normal(0, 50)
        current_price = base_price + variation
        
        open_price = current_price + np.random.uniform(-100, 100)
        high_price = max(current_price, open_price) + np.random.uniform(0, 150)
        low_price = min(current_price, open_price) - np.random.uniform(0, 150)
        previous_close = current_price + np.random.uniform(-200, 200)
        volume = int(np.random.randint(100000, 10000000))
        
        # Present demo timestamps in IST so UI matches expected local times
        server_now = datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=5, minutes=30)))
        market_open_time = server_now.replace(hour=9, minute=15, second=0, microsecond=0)
        market_close_time = server_now.replace(hour=15, minute=30, second=0, microsecond=0)

        if server_now.weekday() < 5 and market_open_time <= server_now <= market_close_time:
            market_status = "[OPEN] (Demo)"
        else:
            market_status = "[CLOSED] (Demo)"

        return {
            'ticker': ticker,
            'company_name': company_name,
            'current_price': round(float(current_price), 2),
            'open_price': round(float(open_price), 2),
            'high_price': round(float(high_price), 2),
            'low_price': round(float(low_price), 2),
            'previous_close': round(float(previous_close), 2),
            'volume': volume,
            'market_status': market_status,
            'last_updated': server_now.strftime("%Y-%m-%d %H:%M:%S %Z"),
            'date': server_now.strftime("%Y-%m-%d"),
            'is_demo': True,
            'is_fallback': bool(is_fallback)
        }
    
    def _generate_demo_historical_data(self, ticker):
        """
        Generate realistic demo historical data for model training.
        
        Parameters:
        -----------
        ticker : str
            Stock ticker symbol
        
        Returns:
        --------
        pd.DataFrame : Mock historical OHLCV data (365 days)
        """
        dates = pd.date_range(end=datetime.now(), periods=365, freq='D')
        
        # Generate realistic price path using random walk
        base_price = 2000
        np.random.seed(hash(ticker) % 2**32)
        returns = np.random.normal(0.0005, 0.02, 365)
        prices = base_price * np.exp(np.cumsum(returns))
        
        data = pd.DataFrame({
            'Date': dates,
            'Open': (prices * (1 + np.random.uniform(-0.01, 0.01, 365))).astype(float),
            'High': (prices * (1 + np.random.uniform(0, 0.02, 365))).astype(float),
            'Low': (prices * (1 + np.random.uniform(-0.02, 0, 365))).astype(float),
            'Close': prices.astype(float),
            'Volume': np.random.randint(1000000, 50000000, 365).astype(int)
        })
        
        # Ensure High >= Close and Low <= Close
        data['High'] = data[['Open', 'High', 'Close']].max(axis=1) * 1.001
        data['Low'] = data[['Open', 'Low', 'Close']].min(axis=1) * 0.999
        
        # Ensure proper data types
        data['Date'] = pd.to_datetime(data['Date'])
        data['Open'] = data['Open'].astype(float)
        data['High'] = data['High'].astype(float)
        data['Low'] = data['Low'].astype(float)
        data['Close'] = data['Close'].astype(float)
        data['Volume'] = data['Volume'].astype(int)
        
        return data
    
    def get_company_ticker(self, company_name):
        """
        Get NSE ticker for a company.
        
        Parameters:
        -----------
        company_name : str
            Company name from config
        
        Returns:
        --------
        dict : {'NSE': ticker, 'BSE': ticker} or None
        """
        if company_name in INDIAN_COMPANIES:
            return INDIAN_COMPANIES[company_name]
        return None
    
    def get_all_companies_list(self):
        """
        Get list of all companies.
        
        Returns:
        --------
        list : Sorted list of company names
        """
        return sorted(list(INDIAN_COMPANIES.keys()))

    def get_supported_companies(self, force_refresh=False, universe='indian'):
        """
        Return a mapping of company name -> ticker info for companies
        that are known to be supported by Yahoo (loaded from a saved
        `live_supported_companies.json`) or from the verified catalog.

        If `force_refresh` is True and the live-supported file is missing,
        attempt to fall back to the verified `yahoo_live_companies.json`.
        """
        try:
            # Choose file paths based on requested universe
            if universe == 'foreign':
                live_file = os.path.join(self.data_path, 'foreign_live_companies.json')
                verified_file = os.path.join(self.data_path, 'foreign_yahoo_live_companies.json')
            else:
                live_file = os.path.join(self.data_path, 'live_supported_companies.json')
                verified_file = os.path.join(self.data_path, 'yahoo_live_companies.json')

            # Try to load the live-supported list if available.
            live_mapping = None
            if os.path.exists(live_file):
                try:
                    with open(live_file, 'r', encoding='utf-8') as fh:
                        names = json.load(fh)
                    if isinstance(names, list) and names:
                        mapping = {}
                        if universe == 'foreign':
                            if isinstance(names, dict):
                                for name, tick in names.items():
                                    if isinstance(tick, str) and not is_blocked_company_name(name):
                                        mapping[name] = {'NSE': tick}
                            else:
                                for entry in names:
                                    if isinstance(entry, dict):
                                        for name, tick in entry.items():
                                            if not is_blocked_company_name(name):
                                                mapping[name] = {'NSE': tick}
                                    elif isinstance(entry, str) and not is_blocked_company_name(entry):
                                        mapping[entry] = {'NSE': entry}
                        else:
                            mapping = {name: ALL_INDIAN_COMPANIES[name] for name in names if name in ALL_INDIAN_COMPANIES and not is_blocked_company_name(name)}
                        if mapping:
                            live_mapping = mapping
                            if not force_refresh:
                                return mapping
                except Exception:
                    pass

            # When Yahoo is unavailable, preserve local live-supported mapping if available.
            if not self._is_yahoo_service_available():
                if live_mapping is not None:
                    return live_mapping

                # If a verified catalog file is present in the repository, use it as a reliable
                # fallback mapping even when Yahoo probes fail (improves Cloud reliability).
                if os.path.exists(verified_file):
                    try:
                        with open(verified_file, 'r', encoding='utf-8') as fh:
                            raw = json.load(fh)
                        mapping = {}
                        if isinstance(raw, dict):
                            if universe == 'foreign':
                                for name, tick_info in raw.items():
                                    if is_blocked_company_name(name):
                                        continue
                                    if isinstance(tick_info, str):
                                        mapping[name] = {'NSE': tick_info}
                                    elif isinstance(tick_info, dict):
                                        t = tick_info.get('ticker') or tick_info.get('TICKER') or tick_info.get('NSE')
                                        if t:
                                            mapping[name] = {'NSE': t}
                            else:
                                for name, tick_info in raw.items():
                                    if is_blocked_company_name(name):
                                        continue
                                    if isinstance(tick_info, dict):
                                        n = {
                                            'NSE': tick_info.get('NSE') or tick_info.get('nse'),
                                            'BSE': tick_info.get('BSE') or tick_info.get('bse') or '999999999.BO',
                                            'sector': tick_info.get('sector', 'General')
                                        }
                                        if n['NSE']:
                                            mapping[name] = n
                                    elif isinstance(tick_info, str):
                                        # raw entry is a plain ticker string
                                        mapping[name] = {'NSE': tick_info}
                        if mapping:
                            return mapping
                    except Exception:
                        # If verified file cannot be read for any reason, continue to try cached data below
                        pass

                cache_data = self._load_availability_cache()
                timestamp = cache_data.get('timestamp')
                supported = cache_data.get('supported_companies')
                if isinstance(supported, list) and supported and isinstance(timestamp, (int, float)):
                    if time.time() - timestamp <= AVAILABILITY_CACHE_TTL:
                        mapping = {}
                        if universe == 'foreign':
                            for entry in supported:
                                if isinstance(entry, dict):
                                    for name, tick in entry.items():
                                        if not is_blocked_company_name(name):
                                            mapping[name] = {'NSE': tick}
                                elif isinstance(entry, str) and not is_blocked_company_name(entry):
                                    mapping[entry] = {'NSE': entry}
                        else:
                            mapping = {name: ALL_INDIAN_COMPANIES[name] for name in supported if name in ALL_INDIAN_COMPANIES and not is_blocked_company_name(name)}
                        return mapping

                return {}

            # If Yahoo is available, use the verified Yahoo catalog when needed
            if os.path.exists(verified_file):
                try:
                    with open(verified_file, 'r', encoding='utf-8') as fh:
                        raw = json.load(fh)
                    mapping = {}
                    if isinstance(raw, dict):
                        for name, tick_info in raw.items():
                            if is_blocked_company_name(name):
                                continue
                            if universe == 'foreign':
                                if isinstance(tick_info, str):
                                    mapping[name] = {'NSE': tick_info}
                                elif isinstance(tick_info, dict):
                                    t = tick_info.get('ticker') or tick_info.get('TICKER') or tick_info.get('NSE')
                                    if t:
                                        mapping[name] = {'NSE': t}
                            else:
                                n = {
                                    'NSE': tick_info.get('NSE') or tick_info.get('nse'),
                                    'BSE': tick_info.get('BSE') or tick_info.get('bse') or '999999999.BO',
                                    'sector': tick_info.get('sector', 'General')
                                }
                                if n['NSE']:
                                    mapping[name] = n
                    if mapping:
                        # Preserve local live-supported entries that may not be present in the verified catalog.
                        if live_mapping is not None:
                            merged_mapping = dict(live_mapping)
                            merged_mapping.update(mapping)
                            self._save_availability_cache(list(merged_mapping.keys()))
                            return merged_mapping
                        self._save_availability_cache(list(mapping.keys()))
                        return mapping
                except Exception:
                    pass

            # If verify refresh failed and we had a local live-supported mapping, use it as a fallback.
            if live_mapping is not None:
                return live_mapping

            return None
        except Exception:
            return None
    
    def fetch_all_live_data(self):
        """
        Fetch live data for all companies (useful for dashboard).
        
        Returns:
        --------
        dict : Company-wise live data
        """
        live_data = {}
        companies = self.get_all_companies_list()
        
        for company in companies:
            ticker_info = self.get_company_ticker(company)
            if ticker_info:
                ticker = ticker_info['NSE']
                data = self.fetch_live_data(ticker)
                if data:
                    live_data[company] = data
        
        return live_data
    
    def validate_data(self, data):
        """
        Validate if data is sufficient for analysis.
        
        Parameters:
        -----------
        data : pd.DataFrame
            Historical data
        
        Returns:
        --------
        bool : True if data is valid
        """
        if data is None or data.empty:
            return False
        
        if len(data) < 50:
            return False
        
        if data.isnull().sum().sum() > 0:
            return False
        
        return True
    
    def cache_data(self, ticker, data, cache_type='historical'):
        """
        Cache data locally to avoid repeated API calls.
        
        Parameters:
        -----------
        ticker : str
            Stock ticker
        data : pd.DataFrame
            Data to cache
        cache_type : str
            Type of cache ('historical' or 'live')
        """
        try:
            cache_file = os.path.join(self.data_path, f"{ticker.replace('.', '_')}_{cache_type}.csv")
            data.to_csv(cache_file, index=False)
        except Exception:
            pass
    
    def load_cached_data(self, ticker, cache_type='historical'):
        """
        Load cached data from local storage.
        
        Parameters:
        -----------
        ticker : str
            Stock ticker
        cache_type : str
            Type of cache ('historical' or 'live')
        
        Returns:
        --------
        pd.DataFrame or None
        """
        try:
            cache_file = os.path.join(self.data_path, f"{ticker.replace('.', '_')}_{cache_type}.csv")
            if os.path.exists(cache_file):
                return pd.read_csv(cache_file)
        except Exception as e:
            print(f"Error loading cached data: {str(e)}")
        
        return None

    def has_local_data(self, ticker=None):
        """Return whether local cached data exists for a ticker or any company."""
        try:
            if ticker:
                cache_file = f"{self.data_path}{ticker.replace('.', '_')}_historical.csv"
                return os.path.exists(cache_file)

            for file_name in os.listdir(self.data_path):
                if file_name.endswith('_historical.csv') or file_name.endswith('_live.csv'):
                    return True
        except Exception:
            pass
        return False


# ==================== EXAMPLE USAGE ====================

def example_usage():
    """Example of how to use DataFetcher"""
    
    fetcher = DataFetcher()
    
    # Get company list
    companies = fetcher.get_all_companies_list()
    print(f"Total companies available: {len(companies)}")
    print(f"First 5 companies: {companies[:5]}")
    
    # Example: Fetch live data for Reliance
    print("\n--- Fetching Live Data ---")
    live_data = fetcher.fetch_live_data('RELIANCE.NS')
    if live_data:
        print(f"Company: {live_data['company_name']}")
        print(f"Current Price: ₹{live_data['current_price']:.2f}")
        print(f"Market Status: {live_data['market_status']}")
    
    # Example: Fetch historical data
    print("\n--- Fetching Historical Data ---")
    hist_data = fetcher.fetch_historical_data('INFY.NS', days=100)
    if hist_data is not None:
        print(f"Data shape: {hist_data.shape}")
        print(f"Date range: {hist_data['Date'].min()} to {hist_data['Date'].max()}")
        print(hist_data.head())


if __name__ == "__main__":
    example_usage()
