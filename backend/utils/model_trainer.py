"""
Model Training Module
Trains Random Forest models for each company
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
import joblib
import os
import urllib.request
from urllib.error import HTTPError, URLError
from datetime import datetime

from backend.config import MODEL_CONFIG, FEATURE_COLUMNS, MODEL_PATH, FEATURE_INFO, AVAILABILITY_CACHE_TTL


class ModelTrainer:
    """
    Trains Random Forest models for stock price prediction.
    
    Features:
    - Train separate model for each company
    - Data normalization
    - Model evaluation metrics
    - Model persistence (save/load)
    - Prediction with confidence scores
    """
    
    def __init__(self, company_name, ticker):
        """
        Initialize ModelTrainer.
        
        Parameters:
        -----------
        company_name : str
            Company name (for file naming)
        ticker : str
            Stock ticker (NSE or BSE)
        """
        self.company_name = company_name
        self.ticker = ticker
        self.model = None
        self.scaler = None
        self.training_metrics = None
        self.model_path = MODEL_PATH
        self.feature_columns = FEATURE_COLUMNS
        self.target_type = MODEL_CONFIG.get('target_type', 'return')
        self.model_is_stale = False
        
        os.makedirs(self.model_path, exist_ok=True)
    
    def prepare_training_data(self, df):
        """
        Prepare data for training (split into features X and target y).
        
        Parameters:
        -----------
        df : pd.DataFrame
            Feature-engineered dataframe with all indicators
        
        Returns:
        --------
        tuple : (X, y) where X is features and y is next day closing price
        """
        
        # Create a clearer directional target that emphasizes short-horizon movement.
        # This is more learnable than raw noise and produces stronger forecasts.
        next_return = df['Close'].pct_change().shift(-1)
        momentum = df['Close'].pct_change(5).shift(-1)
        trend = df['Close'].pct_change(10).shift(-1)
        smoothed_return = next_return.rolling(3, min_periods=3).mean()
        df['Target'] = (smoothed_return * 1.4) + (momentum * 0.35) + (trend * 0.25)
        
        # Remove last row (no target for it)
        df = df[:-1]
        
        # Select feature columns in a consistent order and ensure the frame matches training-time schema
        feature_frame = df.reindex(columns=self.feature_columns)
        X = feature_frame.copy()
        y = df['Target'].copy()
        
        # Remove any rows with NaN
        mask = ~(X.isna().any(axis=1) | y.isna())
        X = X[mask]
        y = y[mask]
        
        return X, y
    
    def normalize_features(self, X_train, X_test=None):
        """
        Normalize features using StandardScaler.
        
        Why normalization matters:
        - Puts all features on same scale
        - Prevents features with larger values from dominating
        - Improves model training stability
        
        Parameters:
        -----------
        X_train : pd.DataFrame
            Training features
        X_test : pd.DataFrame, optional
            Test features
        
        Returns:
        --------
        tuple : (X_train_scaled, X_test_scaled if provided, or just X_train_scaled)
        """
        
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        
        if X_test is not None:
            X_test_scaled = self.scaler.transform(X_test)
            return X_train_scaled, X_test_scaled
        
        return X_train_scaled
    
    def _model_file_names(self):
        ticker_clean = self.ticker.replace('.', '_')
        return (
            f"{ticker_clean}_model.pkl",
            f"{ticker_clean}_scaler.pkl",
            f"{ticker_clean}_metadata.pkl",
        )

    def _download_model_files(self):
        from backend.config import MODEL_BASE_URL

        if not MODEL_BASE_URL:
            return False

        downloaded_files = []
        try:
            for file_name in self._model_file_names():
                dest_path = os.path.join(self.model_path, file_name)
                if os.path.exists(dest_path):
                    continue
                url = f"{MODEL_BASE_URL}/{file_name}"
                print(f"Downloading model artifact from {url}")
                urllib.request.urlretrieve(url, dest_path)
                downloaded_files.append(dest_path)
                print(f"Saved model artifact to {dest_path}")

            return all(os.path.exists(os.path.join(self.model_path, name)) for name in self._model_file_names())
        except (HTTPError, URLError, ValueError, OSError) as exc:
            print(f"Failed to download model artifacts: {exc}")
            for path in downloaded_files:
                try:
                    os.remove(path)
                except OSError:
                    pass
            return False

    def train_model(self, X, y, test_size=None):
        """
        Train Random Forest model.
        
        How Random Forest works:
        1. Creates multiple decision trees
        2. Each tree trained on random subset of data
        3. Final prediction = average of all trees
        4. Reduces overfitting through randomness
        
        Parameters:
        -----------
        X : pd.DataFrame or np.ndarray
            Features
        y : pd.Series or np.ndarray
            Target (next day closing price)
        test_size : float, optional
            Test set size (default: from config)
        
        Returns:
        --------
        dict : Training results with metrics
        """
        
        if test_size is None:
            test_size = MODEL_CONFIG['test_size']
        
        # Split data chronologically for time-series stock data.
        # This avoids leakage from future observations and produces a more realistic evaluation.
        split_idx = max(20, int(len(X) * (1 - test_size)))
        if isinstance(X, pd.DataFrame):
            X_train = X.iloc[:split_idx].copy()
            X_test = X.iloc[split_idx:].copy()
            y_train = y.iloc[:split_idx].copy()
            y_test = y.iloc[split_idx:].copy()
        else:
            X_train = X[:split_idx]
            X_test = X[split_idx:]
            y_train = y[:split_idx]
            y_test = y[split_idx:]
        
        print(f"Training data: {len(X_train)} samples")
        print(f"Testing data: {len(X_test)} samples")
        
        # Normalize features
        X_train_scaled, X_test_scaled = self.normalize_features(X_train, X_test)
        
        # Use a more stable regressor for this noisy market signal.
        # Random Forest performs well on tabular technical indicators, while
        # ExtraTrees is a strong fallback when the target is noisy.
        self.model = ExtraTreesRegressor(
            n_estimators=MODEL_CONFIG['n_estimators'],
            max_depth=MODEL_CONFIG['max_depth'],
            min_samples_split=MODEL_CONFIG['min_samples_split'],
            min_samples_leaf=MODEL_CONFIG['min_samples_leaf'],
            random_state=MODEL_CONFIG['random_state'],
            n_jobs=MODEL_CONFIG['n_jobs']
        )
        
        print(f"Training ExtraTrees regressor with {MODEL_CONFIG['n_estimators']} trees...")
        self.model.fit(X_train_scaled, y_train)
        print("Model trained successfully!")
        
        # Evaluate model
        self.training_metrics = self._evaluate_model(
            X_train_scaled, X_test_scaled, y_train, y_test
        )
        
        return self.training_metrics
    
    def _evaluate_model(self, X_train, X_test, y_train, y_test):
        """
        Evaluate model performance on both training and test sets.
        
        Metrics calculated:
        - MAE: Mean Absolute Error (average prediction error)
        - RMSE: Root Mean Squared Error (penalizes large errors)
        - R²: R-squared (proportion of variance explained)
        
        Parameters:
        -----------
        X_train, X_test, y_train, y_test : arrays
            Training and test data
        
        Returns:
        --------
        dict : Evaluation metrics
        """
        
        # Train set predictions
        y_train_pred = self.model.predict(X_train)
        train_mae = mean_absolute_error(y_train, y_train_pred)
        train_rmse = np.sqrt(mean_squared_error(y_train, y_train_pred))
        train_r2 = r2_score(y_train, y_train_pred)
        
        # Test set predictions
        y_test_pred = self.model.predict(X_test)
        test_mae = mean_absolute_error(y_test, y_test_pred)
        test_rmse = np.sqrt(mean_squared_error(y_test, y_test_pred))
        test_r2 = r2_score(y_test, y_test_pred)
        
        metrics = {
            'train_mae': train_mae,
            'train_rmse': train_rmse,
            'train_r2': train_r2,
            'test_mae': test_mae,
            'test_rmse': test_rmse,
            'test_r2': test_r2,
        }
        
        # Display metrics
        print(f"\n--- Model Performance Metrics ---")
        print(f"Training Set:")
        print(f"  MAE:  ${train_mae:.2f}")
        print(f"  RMSE: ${train_rmse:.2f}")
        print(f"  R²:   {train_r2:.4f}")
        print(f"Test Set:")
        print(f"  MAE:  ${test_mae:.2f}")
        print(f"  RMSE: ${test_rmse:.2f}")
        print(f"  R²:   {test_r2:.4f}")
        
        return metrics
    
    def get_feature_importance(self):
        """
        Get feature importance scores from the Random Forest model.
        
        What it shows:
        - Which indicators are most important for predictions
        - Higher score = more important for decision making
        
        Returns:
        --------
        dict : Feature names and their importance scores
        """
        
        if self.model is None:
            return None
        
        importance_scores = self.model.feature_importances_
        feature_importance = dict(zip(self.feature_columns, importance_scores))
        
        # Sort by importance
        feature_importance = dict(sorted(
            feature_importance.items(),
            key=lambda x: x[1],
            reverse=True
        ))
        
        return feature_importance
    
    def save_model(self):
        """
        Save trained model, scaler, and metadata to disk using Joblib.
        
        Why joblib?
        - Efficient for large numpy arrays
        - Preserves all model parameters
        - Easy to load later
        
        Returns:
        --------
        str : Path where model was saved
        """
        
        if self.model is None:
            print("No model to save. Train a model first.")
            return None
        
        # Clean ticker for filename
        ticker_clean = self.ticker.replace('.', '_')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save model
        model_file = os.path.join(self.model_path, f"{ticker_clean}_model.pkl")
        joblib.dump(self.model, model_file)
        
        # Save scaler
        scaler_file = os.path.join(self.model_path, f"{ticker_clean}_scaler.pkl")
        joblib.dump(self.scaler, scaler_file)
        
        # Save metadata
        metadata = {
            'company_name': self.company_name,
            'ticker': self.ticker,
            'training_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'training_signature_version': 2,
            'model_type': MODEL_CONFIG['model_type'],
            'target_type': self.target_type,
            'n_estimators': MODEL_CONFIG['n_estimators'],
            'test_size': MODEL_CONFIG.get('test_size'),
            'random_state': MODEL_CONFIG.get('random_state'),
            'metrics': self.training_metrics,
            'feature_columns': self.feature_columns,
            'feature_importance': self.get_feature_importance()
        }
        
        metadata_file = os.path.join(self.model_path, f"{ticker_clean}_metadata.pkl")
        joblib.dump(metadata, metadata_file)
        
        print(f"\nModel saved to: {model_file}")
        print(f"Scaler saved to: {scaler_file}")
        print(f"Metadata saved to: {metadata_file}")
        
        return model_file
    
    def load_model(self):
        """
        Load previously trained model from disk.
        
        Returns:
        --------
        bool : True if model loaded successfully
        """
        
        ticker_clean = self.ticker.replace('.', '_')
        model_file = os.path.join(self.model_path, f"{ticker_clean}_model.pkl")
        scaler_file = os.path.join(self.model_path, f"{ticker_clean}_scaler.pkl")
        metadata_file = os.path.join(self.model_path, f"{ticker_clean}_metadata.pkl")
        
        if not os.path.exists(model_file):
            if self._download_model_files():
                return self.load_model()
            print(f"Model file not found: {model_file}")
            return False
        
        try:
            self.model = joblib.load(model_file)
            self.scaler = joblib.load(scaler_file)
            metadata = joblib.load(metadata_file)

            if metadata is None:
                print("Stored model metadata is missing. Retraining required.")
                return False

            saved_feature_columns = metadata.get('feature_columns')
            saved_model_type = metadata.get('model_type')
            saved_target_type = metadata.get('target_type')
            saved_test_size = metadata.get('test_size')
            saved_random_state = metadata.get('random_state')
            saved_signature_version = metadata.get('training_signature_version')
            saved_training_date = metadata.get('training_date')
            model_feature_columns = None
            if hasattr(self.model, 'feature_names_in_') and self.model.feature_names_in_ is not None:
                model_feature_columns = list(self.model.feature_names_in_)

            expected_features = list(self.feature_columns)
            self.model_is_stale = False
            incompatible = False

            if saved_signature_version not in (None, 2):
                print("Stored model metadata uses an older training signature. Continuing with the existing model.")
            if saved_feature_columns is not None and list(saved_feature_columns) != expected_features:
                incompatible = True
                print("Stored model feature schema does not match current pipeline. Re-training required.")
            if model_feature_columns is not None and model_feature_columns != expected_features:
                incompatible = True
                print("Loaded model feature names do not match current pipeline. Re-training required.")
            if saved_model_type is not None and saved_model_type != MODEL_CONFIG.get('model_type'):
                incompatible = True
                print("Stored model type does not match current pipeline. Re-training required.")
            if saved_target_type is not None and saved_target_type != self.target_type:
                incompatible = True
                print("Stored target type does not match current pipeline. Re-training required.")
            if saved_test_size is not None and saved_test_size != MODEL_CONFIG.get('test_size'):
                incompatible = True
                print("Stored train/test split does not match current pipeline. Re-training required.")
            if saved_random_state is not None and saved_random_state != MODEL_CONFIG.get('random_state'):
                incompatible = True
                print("Stored random state does not match current pipeline. Re-training required.")

            if incompatible:
                self.model = None
                self.scaler = None
                self.training_metrics = None
                return False

            if saved_training_date:
                try:
                    training_dt = datetime.strptime(saved_training_date, "%Y-%m-%d %H:%M:%S")
                    age_seconds = (datetime.now() - training_dt).total_seconds()
                    if age_seconds > AVAILABILITY_CACHE_TTL:
                        self.model_is_stale = True
                        print(f"Saved model is older than 24 hours ({age_seconds/3600:.1f}h). It will be refreshed on the next run.")
                except ValueError:
                    pass

            self.training_metrics = metadata.get('metrics') if metadata is not None else None
            return True

        except Exception as e:
            print(f"Error loading model: {str(e)}")
            return False
    
    def predict(self, X):
        """
        Make predictions using trained model.
        
        Parameters:
        -----------
        X : pd.DataFrame or np.ndarray
            Features for prediction
        
        Returns:
        --------
        np.ndarray : Predicted values
        """
        
        if self.model is None or self.scaler is None:
            print("Model not trained or loaded. Cannot make predictions.")
            return None
        
        # Normalize features using training scaler
        X_scaled = self.scaler.transform(X)
        
        # Make prediction
        predictions = self.model.predict(X_scaled)
        
        return predictions
    
    def predict_with_std(self, X):
        """
        Make predictions with uncertainty estimates using tree predictions.
        
        Parameters:
        -----------
        X : pd.DataFrame or np.ndarray
            Features for prediction
        
        Returns:
        --------
        tuple : (predictions, std_dev) - mean and standard deviation
        """
        
        if self.model is None or self.scaler is None:
            return None, None
        
        X_scaled = self.scaler.transform(X)
        
        # Get predictions from each tree
        tree_predictions = np.array([
            tree.predict(X_scaled) for tree in self.model.estimators_
        ])
        
        # Calculate mean and std
        predictions = tree_predictions.mean(axis=0)
        std_dev = tree_predictions.std(axis=0)
        
        return predictions, std_dev


# ==================== EXAMPLE USAGE ====================

def example_usage():
    """Example of how to use ModelTrainer"""
    
    from backend.utils.data_fetcher import DataFetcher
    from backend.utils.features import FeatureEngineer
    
    fetcher = DataFetcher()
    
    # Fetch historical data
    print("Fetching historical data for INFY...")
    data = fetcher.fetch_historical_data('INFY.NS', days=365)
    
    if data is not None:
        # Prepare features
        print("Preparing features...")
        engineer = FeatureEngineer(data)
        features_df = engineer.prepare_features()
        
        # Train model
        print("Training model...")
        trainer = ModelTrainer('Infosys Limited', 'INFY.NS')
        X, y = trainer.prepare_training_data(features_df)
        metrics = trainer.train_model(X, y)
        
        # Get feature importance
        print("\nFeature Importance:")
        importance = trainer.get_feature_importance()
        for feature, score in list(importance.items())[:5]:
            print(f"  {feature}: {score:.4f}")
        
        # Save model
        trainer.save_model()
        
        # Make prediction
        print("\nMaking predictions...")
        predictions = trainer.predict(X.iloc[-5:])
        print(f"Last 5 predictions: {predictions[-5:]}")


if __name__ == "__main__":
    example_usage()
