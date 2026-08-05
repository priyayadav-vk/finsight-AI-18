from config import INDIAN_COMPANIES
from utils.data_fetcher import DataFetcher
from utils.features import FeatureEngineer
from utils.model_checker import ModelChecker
from utils.model_predictor import ModelPredictor

checker = ModelChecker()
for company_name, company_info in sorted(INDIAN_COMPANIES.items()):
    if company_name != '3M India Limited':
        continue
    for exchange in ('NSE', 'BSE'):
        ticker = company_info.get(exchange)
        if not ticker or not checker.has_model(ticker):
            continue
        print('company', company_name, exchange, ticker)
        try:
            fetcher = DataFetcher()
            historical = fetcher.fetch_historical_data(ticker, days=365)
            features = FeatureEngineer(historical).prepare_features()
            predictor = ModelPredictor(company_name, ticker)
            print('load result', predictor.load_model())
            result = predictor.predict_next_price(features)
            print('prediction', result is not None, result.get('predicted_price') if result else None)
            analysis = predictor.get_full_analysis(features, {'current_price': result['current_price']}, 0.02)
            print('analysis has signal', bool(analysis and analysis.get('signal')))
        except Exception as exc:
            print('ERROR', repr(exc))
            raise
