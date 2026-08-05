from backend.utils.model_trainer import ModelTrainer
from backend.utils.features import FeatureEngineer
import pandas as pd, os, sys

csv_path = r"C:\Users\dell\OneDrive\Desktop\finsightai\data\TCS_NS_historical.csv"
if not os.path.exists(csv_path):
    print('ERROR: CSV not found at', csv_path)
    sys.exit(2)
print('Loading CSV:', csv_path)
df = pd.read_csv(csv_path)
print('Rows in CSV:', len(df))

# Prepare features
engineer = FeatureEngineer(df)
features_df = engineer.prepare_features()
print('Feature dataframe shape:', features_df.shape)

# Train
trainer = ModelTrainer('Tata Consultancy Services', 'TCS.NS')
X, y = trainer.prepare_training_data(features_df)
print('Prepared X,y shapes:', X.shape, y.shape)
metrics = trainer.train_model(X, y)
print('Training metrics:', metrics)
model_file = trainer.save_model()
print('Model saved to:', model_file)
