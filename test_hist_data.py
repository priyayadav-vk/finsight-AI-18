"""Test historical data fetching for predictions"""
import sys
sys.path.insert(0, 'C:\\Users\\dell\\OneDrive\\Desktop\\finsightai')

from utils.data_fetcher import DataFetcher

fetcher = DataFetcher()

print('[TEST] Fetching historical data for TCS.NS...\n')

hist_data = fetcher.fetch_historical_data('TCS.NS', days=365)

if hist_data is not None:
    print(f'[SUCCESS] Got historical data')
    print(f'  Shape: {hist_data.shape}')
    print(f'  Columns: {list(hist_data.columns)}')
    print(f'  Date range: {hist_data["Date"].min()} to {hist_data["Date"].max()}')
    print()
    print('First 5 rows:')
    print(hist_data.head())
else:
    print('[ERROR] hist_data is None')
