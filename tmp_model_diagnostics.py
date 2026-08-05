from utils.data_fetcher import DataFetcher
from utils.features import FeatureEngineer
from utils.model_trainer import ModelTrainer
from sklearn.ensemble import RandomForestRegressor, ExtraTreesRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import numpy as np


ticker='RELIANCE.NS'
df = DataFetcher().fetch_historical_data(ticker, days=900)
features = FeatureEngineer(df).prepare_features()
trainer = ModelTrainer('Demo', ticker)
X, y = trainer.prepare_training_data(features)
print('shape', X.shape, y.shape)

models = [
    ('rf', RandomForestRegressor(n_estimators=200, max_depth=10, random_state=42, n_jobs=-1)),
    ('extratrees', ExtraTreesRegressor(n_estimators=300, max_depth=12, random_state=42, n_jobs=-1)),
    ('gboost', GradientBoostingRegressor(random_state=42)),
    ('ridge', Ridge(alpha=1.0)),
]

for name, model in models:
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, shuffle=False)
    if name == 'ridge':
        X_train2 = X_train
        X_test2 = X_test
    else:
        X_train2, X_test2 = trainer.normalize_features(X_train, X_test)
    model.fit(X_train2, y_train)
    pred = model.predict(X_test2)
    print(name, 'r2', round(float(r2_score(y_test, pred)), 6), 'mae', round(float(mean_absolute_error(y_test, pred)), 6), 'rmse', round(float(np.sqrt(mean_squared_error(y_test, pred))), 6))
