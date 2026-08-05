from utils.data_fetcher import DataFetcher
from utils.features import FeatureEngineer
from utils.model_predictor import ModelPredictor

for ticker in ['RELIANCE.NS', 'TCS.NS', 'INFY.NS']:
    fetcher = DataFetcher()
    hist = fetcher.fetch_historical_data(ticker, days=365)
    features = FeatureEngineer(hist).prepare_features()
    predictor = ModelPredictor('Demo', ticker)
    loaded = predictor.load_model()
    print(ticker, 'loaded', loaded)
    if loaded:
        live = fetcher.fetch_live_data(ticker)
        analysis = predictor.get_full_analysis(features, live, threshold=0.02)
        print(' ', analysis['signal']['signal'], analysis['signal']['confidence'], analysis['prediction']['predicted_return'])
    else:
        X, y = predictor.trainer.prepare_training_data(features)
        predictor.trainer.train_model(X, y)
        predictor.trainer.save_model()
        live = fetcher.fetch_live_data(ticker)
        analysis = predictor.get_full_analysis(features, live, threshold=0.02)
        print(' ', analysis['signal']['signal'], analysis['signal']['confidence'], analysis['prediction']['predicted_return'])
