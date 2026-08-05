import requests
import pandas as pd

WIKI_URL = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
headers = {'User-Agent': 'Mozilla/5.0'}
resp = requests.get(WIKI_URL, headers=headers, timeout=30)
resp.raise_for_status()
html = resp.text
print('fetched', len(html), 'chars')
try:
    tables = pd.read_html(html)
    print('tables found:', len(tables))
    for i, t in enumerate(tables[:3], start=1):
        print('Table', i, 'columns:', list(t.columns) )
except Exception as e:
    print('pd.read_html failed:', e)
