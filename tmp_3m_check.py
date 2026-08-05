import json, traceback
from config import INDIAN_COMPANIES
from utils.data_fetcher import DataFetcher
from utils.features import FeatureEngineer
from utils.model_predictor import ModelPredictor

company_name = '3M India Limited'
print('Company:', company_name)
info = INDIAN_COMPANIES.get(company_name)
if not info:
    print('Company not found in INDIAN_COMPANIES')
    raise SystemExit(1)

fetcher = DataFetcher()
results = {}

for exchange in ('NSE','BSE'):
    ticker = info.get(exchange)
    if not ticker:
        results[exchange] = {'error': 'No ticker configured'}
        continue
    try:
        print('\n---', exchange, ticker)
        hist = fetcher.fetch_historical_data(ticker, days=365)
        if hist is None or hist.empty:
            results[exchange] = {'error': 'No historical data returned (demo fallback?)'}
            continue
        features = FeatureEngineer(hist).prepare_features()
        pred = ModelPredictor(company_name, ticker)
        loaded = pred.load_model()
        results[exchange] = {'ticker': ticker, 'model_loaded': bool(loaded)}
        if not loaded:
            results[exchange]['note'] = 'Model not loaded; predictions skipped'
            continue
        prediction = pred.predict_next_price(features)
        results[exchange]['prediction'] = prediction
        analysis = pred.get_full_analysis(features, {'current_price': prediction['current_price']}, threshold=0.02)
        results[exchange]['analysis_signal'] = analysis.get('signal') if analysis else None
    except Exception as e:
        results[exchange] = {'error': str(e), 'trace': traceback.format_exc()}

print(json.dumps(results, default=str, indent=2))
