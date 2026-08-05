import os
import shutil
import tempfile
import unittest
from datetime import datetime, timedelta

import joblib
import numpy as np

from config import FEATURE_COLUMNS
from utils.model_trainer import ModelTrainer


class DummyModel:
    def __init__(self):
        self.feature_names_in_ = FEATURE_COLUMNS
        self.feature_importances_ = np.array([0.1] * len(FEATURE_COLUMNS))

    def predict(self, X):
        return np.ones(len(X))


class DummyScaler:
    def transform(self, X):
        return X


class TestModelTrainerStaleModel(unittest.TestCase):
    def test_load_model_allows_stale_models_but_marks_them_stale(self):
        temp_dir = tempfile.mkdtemp(prefix="model-trainer-test-", dir=".")
        try:
            trainer = ModelTrainer("Test Company", "TEST.NS")
            trainer.model_path = temp_dir
            trainer.model = DummyModel()
            trainer.scaler = DummyScaler()
            trainer.training_metrics = {"test_r2": 0.5}
            trainer.save_model()

            metadata_file = os.path.join(temp_dir, "TEST_NS_metadata.pkl")
            metadata = joblib.load(metadata_file)
            old_date = (datetime.now() - timedelta(hours=25)).strftime("%Y-%m-%d %H:%M:%S")
            metadata["training_date"] = old_date
            joblib.dump(metadata, metadata_file)

            fresh_trainer = ModelTrainer("Test Company", "TEST.NS")
            fresh_trainer.model_path = temp_dir

            loaded = fresh_trainer.load_model()

            self.assertTrue(loaded)
            self.assertTrue(fresh_trainer.model_is_stale)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_load_model_rejects_incompatible_feature_schema(self):
        temp_dir = tempfile.mkdtemp(prefix="model-trainer-test-", dir=".")
        try:
            trainer = ModelTrainer("Test Company", "TEST.NS")
            trainer.model_path = temp_dir
            trainer.model = DummyModel()
            trainer.scaler = DummyScaler()
            trainer.training_metrics = {"test_r2": 0.5}
            trainer.save_model()

            metadata_file = os.path.join(temp_dir, "TEST_NS_metadata.pkl")
            metadata = joblib.load(metadata_file)
            metadata["feature_columns"] = ["MA10", "MA20", "EMA10", "EMA20"]
            joblib.dump(metadata, metadata_file)

            fresh_trainer = ModelTrainer("Test Company", "TEST.NS")
            fresh_trainer.model_path = temp_dir

            loaded = fresh_trainer.load_model()

            self.assertFalse(loaded)
            self.assertFalse(fresh_trainer.model_is_stale)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
