from utils.data_fetcher import DataFetcher
import json, traceback

fetcher = DataFetcher()

def safe_run(name, fn, *args, **kwargs):
    try:
        res = fn(*args, **kwargs)
        # For DataFrames, show shape and head
        if hasattr(res, 'shape'):
            out = {'type': 'dataframe', 'shape': res.shape, 'head': res.head().to_dict(orient='list')}
        else:
            out = res
        print(json.dumps({'name': name, 'ok': True, 'result': out}, default=str, indent=2))
    except Exception as e:
        print(json.dumps({'name': name, 'ok': False, 'error': str(e), 'trace': traceback.format_exc()}, indent=2))

# Test tickers
tickers = ["3MINDIA.NS", "500002.BO"]

for t in tickers:
    print('\n=== TICKER: %s ===' % t)
    safe_run(f'{t} - check_status', fetcher.check_yahoo_status, t)
    safe_run(f'{t} - fetch_live', fetcher.fetch_live_data, t)
    safe_run(f'{t} - fetch_hist_30d', fetcher.fetch_historical_data, t, 30)

print('\nDone')
