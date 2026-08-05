import traceback, json
from pages import charts
from utils.data_fetcher import DataFetcher

print('Running plotly/chart rendering checks...')
fetcher = DataFetcher()
# Use 3M India NSE ticker
ticker = '3MINDIA.NS'
try:
    hist = fetcher.fetch_historical_data(ticker, days=365)
    if hist is None or hist.empty:
        raise SystemExit('No historical data')
    # Prepare features
    from utils.features import FeatureEngineer
    features = FeatureEngineer(hist).prepare_features()
    funcs = [
        charts.create_candlestick_chart,
        charts.create_volume_chart,
        charts.create_moving_average_chart,
        charts.create_rsi_chart,
        charts.create_macd_chart,
        charts.create_bollinger_bands_chart,
        charts.create_volatility_chart
    ]
    results = {}
    for fn in funcs:
        name = fn.__name__
        try:
            fig = fn(features)
            # Basic checks
            ok = hasattr(fig, 'to_html') and hasattr(fig, 'data')
            results[name] = {'ok': True, 'data_traces': len(fig.data)}
        except Exception as e:
            results[name] = {'ok': False, 'error': str(e), 'trace': traceback.format_exc()}
    print(json.dumps(results, indent=2))
except Exception as e:
    print('FAILED', str(e))
    print(traceback.format_exc())
