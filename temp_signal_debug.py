from utils.model_predictor import ModelPredictor
from utils.data_fetcher import DataFetcher
from utils.features import FeatureEngineer
from config import THRESHOLD_OPTIONS

ticker = '3MINDIA.NS'
company = '3M India Limited'
fetcher = DataFetcher()

live_data = fetcher.fetch_live_data(ticker)
print('live_data current_price', live_data.get('current_price'))

hist = fetcher.fetch_historical_data(ticker, days=365)
features = FeatureEngineer(hist).prepare_features()
predictor = ModelPredictor(company, ticker)
loaded = predictor.load_model()
print('loaded', loaded)
if not loaded:
    X, y = predictor.trainer.prepare_training_data(features)
    predictor.trainer.train_model(X, y)

prediction = predictor.predict_next_price(features)
print('predict_next_price', prediction)

analysis = predictor.get_full_analysis(features, live_data, THRESHOLD_OPTIONS['2%'])
print('analysis prediction', analysis['prediction'])
print('analysis signal', analysis['signal'])
print('prediction_data current_price', analysis['prediction']['current_price'])
print('raw live current_price', live_data.get('current_price'))
print('threshold used', analysis['signal']['threshold_used'])
print('confidence', analysis['signal']['confidence'])
