from utils.model_predictor import ModelPredictor
from utils.data_fetcher import DataFetcher
from utils.features import FeatureEngineer
from config import THRESHOLD_OPTIONS

fetcher = DataFetcher()
for ticker in ['RELIANCE.NS', 'INFY.NS', 'HDFC.NS', 'SBIN.NS']:
    print('===', ticker)
    hist = fetcher.fetch_historical_data(ticker, days=365)
    features = FeatureEngineer(hist).prepare_features()
    predictor = ModelPredictor(ticker.split('.')[0], ticker)
    loaded = predictor.load_model()
    if not loaded:
        X, y = predictor.trainer.prepare_training_data(features)
        predictor.trainer.train_model(X, y)
    prediction = predictor.predict_next_price(features)
    if prediction is None:
        print('prediction failed')
        continue
    print('predicted change', prediction['change_percent'], 'confidence', prediction['confidence'])
    for name, threshold_val in THRESHOLD_OPTIONS.items():
        threshold = 0.02 if threshold_val is None else threshold_val
        signal = predictor.generate_signal(prediction, threshold)
        print(' ', name, signal['signal'], signal['reason'])
