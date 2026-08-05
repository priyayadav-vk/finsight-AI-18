from utils.data_fetcher import DataFetcher
from utils.features import FeatureEngineer
from utils.model_trainer import ModelTrainer

ticker='RELIANCE.NS'
fetcher=DataFetcher()
hist=fetcher.fetch_historical_data(ticker, days=365)
features=FeatureEngineer(hist).prepare_features()
trainer=ModelTrainer('Reliance Industries Limited', ticker)
X,y=trainer.prepare_training_data(features)
print('rows', len(X))
for ts in [0.05,0.1,0.125,0.15,0.17,0.18,0.2,0.22,0.25,0.3]:
    m=trainer.train_model(X,y,test_size=ts)
    print(f'ts={ts:.3f} train_r2={m["train_r2"]:.4f} test_r2={m["test_r2"]:.4f} test_mae={m["test_mae"]:.5f} test_rmse={m["test_rmse"]:.5f}')
