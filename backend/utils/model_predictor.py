"""
Model Predictor Module
Makes stock price predictions and generates trading signals
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

from backend.utils.model_trainer import ModelTrainer
from backend.utils.features import FeatureEngineer
from backend.utils.enhanced_predictor import EnhancedPredictor
from backend.config import RECOMMENDATIONS, RISK_LEVELS, THRESHOLD_OPTIONS, DEFAULT_THRESHOLD


class ModelPredictor:
    """
    Uses trained Random Forest model to make predictions and generate signals.
    
    Features:
    - Load trained models
    - Make price predictions
    - Generate BUY/HOLD/SELL signals
    - Calculate confidence scores
    - Risk assessment
    - Prediction history tracking
    """
    
    def __init__(self, company_name, ticker):
        """
        Initialize ModelPredictor.
        
        Parameters:
        -----------
        company_name : str
            Company name
        ticker : str
            Stock ticker
        """
        self.company_name = company_name
        self.ticker = ticker
        self.trainer = ModelTrainer(company_name, ticker)
        self.last_prediction = None
        self.prediction_history = []
    
    def load_model(self):
        """
        Load pre-trained model for this company.
        
        Returns:
        --------
        bool : True if model loaded successfully
        """
        return self.trainer.load_model()
    
    def predict_next_price(self, features_df, current_price_override=None, latest_volatility=None):
        """
        Predict the next day's return and convert it to a price forecast.
        
        IMPROVEMENTS:
        - Better trend signal weighting
        - More reasonable return clipping
        - Improved confidence calculation
        - Better handling of extreme predictions
        
        Parameters:
        -----------
        features_df : pd.DataFrame
            Feature-engineered data with all indicators
        current_price_override : float, optional
            Live current price to align the forecast
        latest_volatility : float, optional
            Latest historical volatility for confidence normalization
        
        Returns:
        --------
        dict : Prediction details including price targets
        """
        
        if self.trainer.model is None:
            return None
        
        # Get last row (today's data)
        last_row = features_df.iloc[-1:]
        
        # Extract features in the exact same order and schema used during training.
        X = last_row.reindex(columns=self.trainer.feature_columns).copy()
        
        # Make prediction
        predicted_target = self.trainer.predict(X)[0]
        
        # Get confidence (std dev from multiple trees)
        _, std_dev = self.trainer.predict_with_std(X)
        std_dev_value = float(std_dev[0]) if std_dev is not None else 0.0

        # Use the live market price as the baseline whenever it is available.
        current_price = float(last_row['Close'].values[0])
        if current_price_override is not None:
            current_price = float(current_price_override)
        elif 'current_price' in last_row.columns:
            current_price = float(last_row['current_price'].values[0])

        if self.trainer.target_type == 'return':
            predicted_return = float(predicted_target)
            
            # ==================== IMPROVED TREND BLENDING ====================
            latest = features_df.iloc[-1]
            trend_signal = 0.0
            
            # Moving Average Crossover Signal (weight: 0.25)
            if 'MA10' in latest and 'MA20' in latest:
                ma_diff = (latest['MA10'] - latest['MA20']) / max(latest['MA20'], 1.0)
                trend_signal += ma_diff * 0.25  # Bullish if MA10 > MA20
            
            # RSI Signal (weight: 0.20) - oversold/overbought
            if 'RSI' in latest:
                rsi_signal = (50 - latest['RSI']) / 100.0  # Positive when RSI < 50
                trend_signal += rsi_signal * 0.20
            
            # MACD Histogram (weight: 0.15)
            if 'MACD_Hist' in latest:
                macd_norm = latest['MACD_Hist'] / max(abs(latest.get('MACD_Signal', 1.0)), 1.0)
                trend_signal += macd_norm * 0.15
            
            # Daily Return Momentum (weight: 0.20)
            if 'Daily_Return' in latest:
                trend_signal += latest['Daily_Return'] * 0.20
            
            # ==================== REFINED RETURN CALCULATION ====================
            # Better blending: 60% model + 40% trend signal
            blended_return = (predicted_return * 0.60) + (trend_signal * 0.40)
            
            # More reasonable clipping: -15% to +15% instead of -25% to +25%
            # This prevents extreme unrealistic predictions
            predicted_return = float(np.clip(blended_return, -0.15, 0.15))
            
            predicted_price = current_price * (1 + predicted_return)
            price_change = predicted_price - current_price
            change_percent = predicted_return * 100
        else:
            predicted_price = float(predicted_target)
            price_change = predicted_price - current_price
            change_percent = (price_change / current_price) * 100
            predicted_return = change_percent / 100

        # ==================== IMPROVED CONFIDENCE CALCULATION ====================
        # Confidence should reflect:
        # 1. Model uncertainty (std_dev)
        # 2. Prediction magnitude (big moves are harder to predict)
        # 3. Market volatility
        
        if self.trainer.target_type == 'return':
            volatility_scale = max(float(latest_volatility) if latest_volatility is not None else 0.02, 0.01)
            confidence_scale = max(abs(predicted_return), volatility_scale * 0.8, 0.003)
        else:
            confidence_scale = max(abs(current_price), 1.0)

        # Base confidence from model uncertainty
        ratio = std_dev_value / confidence_scale if confidence_scale > 0 else 1.0
        base_confidence = np.clip(1.0 / (1.0 + ratio), 0.01, 0.99)
        
        # Boost confidence for moderate predictions (not too big, not too small)
        if abs(predicted_return) > 0.03:
            confidence = base_confidence + 0.15  # Moderate boost
        elif abs(predicted_return) > 0.015:
            confidence = base_confidence + 0.20  # Good boost
        elif abs(predicted_return) > 0.008:
            confidence = base_confidence + 0.12
        elif abs(predicted_return) > 0.003:
            confidence = base_confidence + 0.06
        else:
            confidence = base_confidence + 0.02
        
        # Keep confidence in reasonable range
        confidence = float(np.clip(confidence, 0.40, 0.95))
        
        prediction_result = {
            'ticker': self.ticker,
            'company_name': self.company_name,
            'current_price': round(current_price, 2),
            'predicted_price': round(predicted_price, 2),
            'price_change': round(price_change, 2),
            'change_percent': round(change_percent, 2),
            'predicted_return': round(predicted_return, 4),
            'confidence': round(confidence, 3),
            'prediction_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'std_dev': round(float(std_dev[0]) if std_dev is not None else 0, 6),
            'trend_signal_strength': round(trend_signal if 'trend_signal' in locals() else 0, 3)
        }
        
        self.last_prediction = prediction_result
        
        return prediction_result
    
    def generate_signal(self, prediction, threshold=None, volatility=None):
        """
        Generate BUY/HOLD/SELL signal based on prediction.
        
        IMPROVED LOGIC:
        - Stricter thresholds for BUY/SELL signals
        - HOLD is default for uncertain cases
        - Confidence must be adequate for directional signals
        - Uses asymmetric confidence gates
        
        Parameters:
        -----------
        prediction : dict
            Prediction result from predict_next_price()
        threshold : float, optional
            Decimal threshold (e.g., 0.02 for 2%)
        volatility : float, optional
            Latest historical volatility used for auto thresholding
        
        Returns:
        --------
        dict : Signal and recommendation
        """
        
        if prediction is None:
            return None
        
        if threshold is None or not isinstance(threshold, (int, float)):
            volatility = float(volatility) if volatility is not None else 0.0
            threshold = max(DEFAULT_THRESHOLD, volatility * 1.2)
            threshold = max(threshold, 0.0025)

        predicted_return = float(prediction.get('predicted_return', 0.0))
        confidence = float(prediction.get('confidence', 0.0))
        display_percent = predicted_return * 100.0
        
        # ==================== IMPROVED SIGNAL LOGIC ====================
        # More conservative: require stronger signals for BUY/SELL
        
        # GATE 1: Very low confidence always results in HOLD
        if confidence < 0.45:
            signal = "HOLD"
            reason = (
                f"Low confidence ({confidence:.1%}); holding position. "
                f"Expected return {display_percent:.2f}%"
            )
        
        # GATE 2: Neutral zone (no clear signal)
        elif abs(predicted_return) <= threshold * 0.4:
            signal = "HOLD"
            reason = f"Neutral: Expected return {display_percent:.2f}% is within tight band"
        
        # GATE 3: STRONG BUY signal (high confidence + positive return)
        elif predicted_return >= threshold * 1.3:
            if confidence >= 0.60:
                signal = "BUY"
                reason = (
                    f"STRONG BUY: Expected return {display_percent:.2f}% with high confidence {confidence:.1%}. "
                    f"Threshold: {threshold*100:.2f}%"
                )
            elif predicted_return >= threshold * 1.8:
                signal = "BUY"
                reason = (
                    f"BUY: Very strong expected return {display_percent:.2f}% (extreme confidence not required). "
                    f"Threshold: {threshold*100:.2f}%"
                )
            else:
                signal = "HOLD"
                reason = f"Signal emerging but confidence {confidence:.1%} not sufficient. Expected {display_percent:.2f}%"
        
        # GATE 4: STRONG SELL signal (high confidence + negative return)
        elif predicted_return <= -threshold * 1.3:
            if confidence >= 0.60:
                signal = "SELL"
                reason = (
                    f"STRONG SELL: Expected downside {display_percent:.2f}% with confidence {confidence:.1%}. "
                    f"Threshold: {threshold*100:.2f}%"
                )
            elif predicted_return <= -threshold * 1.8:
                signal = "SELL"
                reason = (
                    f"SELL: Strong downside {display_percent:.2f}% expected. "
                    f"Threshold: {threshold*100:.2f}%"
                )
            else:
                signal = "HOLD"
                reason = f"Weak sell signal. Confidence {confidence:.1%} insufficient"
        
        # GATE 5: Moderate BUY (positive but weaker)
        elif 0 < predicted_return < threshold * 1.3:
            if confidence >= 0.70:
                signal = "BUY"
                reason = f"Moderate BUY: Positive return {display_percent:.2f}% with excellent confidence {confidence:.1%}"
            else:
                signal = "HOLD"
                reason = f"Weak buy signal ({display_percent:.2f}%) waiting for better entry"
        
        # GATE 6: Moderate SELL (negative but weaker)
        else:  # predicted_return < 0
            if confidence >= 0.70:
                signal = "SELL"
                reason = f"Moderate SELL: Expected downside {display_percent:.2f}% with confidence {confidence:.1%}"
            else:
                signal = "HOLD"
                reason = f"Weak sell signal ({display_percent:.2f}%) holding position"
        
        signal_result = {
            'signal': signal,
            'recommendation': RECOMMENDATIONS.get(signal, "No recommendation"),
            'reason': reason,
            'threshold_used': threshold,
            'confidence': confidence,
            'expected_return_percent': display_percent,
            'signal_strength': self._calculate_signal_strength(predicted_return, confidence, threshold)
        }
        
        return signal_result
    
    def _calculate_signal_strength(self, predicted_return, confidence, threshold):
        """
        Calculate how strong the signal is (0-100 scale).
        
        Parameters:
        -----------
        predicted_return : float
            Predicted return as decimal
        confidence : float
            Model confidence (0-1)
        threshold : float
            Signal threshold
            
        Returns:
        --------
        int : Signal strength 0-100
        """
        # Normalize return relative to threshold
        normalized_return = abs(predicted_return) / max(threshold, 0.001)
        
        # Signal strength = 50% from return strength + 50% from confidence
        return_strength = min(normalized_return * 50, 50)  # 0-50
        confidence_strength = confidence * 50  # 0-50
        
        total_strength = int(return_strength + confidence_strength)
        return np.clip(total_strength, 0, 100)
    
    def assess_risk(self, features_df, current_price):
        """
        Assess risk level based on technical indicators.
        
        Risk factors considered:
        1. Volatility (high volatility = high risk)
        2. RSI levels (overbought/oversold = high risk)
        3. Bollinger Bands position (at edges = high risk)
        4. MACD histogram (divergence = high risk)
        
        Parameters:
        -----------
        features_df : pd.DataFrame
            Feature-engineered data
        current_price : float
            Current closing price
        
        Returns:
        --------
        dict : Risk assessment
        """
        
        latest = features_df.iloc[-1]
        
        risk_score = 0.0  # 0-1 scale
        risk_factors = []
        
        # Factor 1: Volatility (weight: 0.3)
        volatility = latest['Volatility']
        if volatility > 0.03:
            risk_score += 0.3
            risk_factors.append(f"High volatility: {volatility:.4f}")
        elif volatility > 0.02:
            risk_score += 0.15
        
        # Factor 2: RSI levels (weight: 0.25)
        rsi = latest['RSI']
        if rsi > 70 or rsi < 30:
            risk_score += 0.25
            status = "OVERBOUGHT" if rsi > 70 else "OVERSOLD"
            risk_factors.append(f"RSI {status}: {rsi:.2f}")
        
        # Factor 3: Bollinger Bands position (weight: 0.2)
        bb_high = latest['BB_High']
        bb_low = latest['BB_Low']
        price_position = (current_price - bb_low) / (bb_high - bb_low)
        
        if price_position > 0.9 or price_position < 0.1:
            risk_score += 0.2
            location = "Upper band" if price_position > 0.9 else "Lower band"
            risk_factors.append(f"Price at {location}")
        
        # Factor 4: MACD divergence (weight: 0.25)
        macd_hist = latest['MACD_Hist']
        if abs(macd_hist) > latest['MACD'] * 0.5:
            risk_score += 0.15
            risk_factors.append("MACD divergence detected")
        
        # Determine risk level
        if risk_score > 0.6:
            risk_level = "HIGH"
        elif risk_score > 0.35:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        risk_assessment = {
            'risk_level': risk_level,
            'risk_score': min(risk_score, 1.0),
            'risk_emoji': RISK_LEVELS[risk_level],
            'risk_factors': risk_factors if risk_factors else ["Stable conditions"]
        }
        
        return risk_assessment
    
    def get_full_analysis(self, features_df, live_data, threshold=None):
        """
        Get complete analysis: prediction, signal, risk, and metrics.
        
        Parameters:
        -----------
        features_df : pd.DataFrame
            Feature-engineered data
        live_data : dict
            Current market data
        threshold : float, optional
            Prediction threshold
        
        Returns:
        --------
        dict : Complete analysis
        """
        
        # Determine live current price if available
        live_current_price = None
        if live_data is not None and 'current_price' in live_data:
            try:
                live_current_price = float(live_data['current_price'])
            except (TypeError, ValueError):
                live_current_price = None

        # Get latest volatility for confidence scaling and thresholding
        latest_volatility = None
        if 'Volatility' in features_df.columns:
            latest_volatility = float(features_df.iloc[-1]['Volatility'])

        # Make prediction aligned to latest price
        prediction = self.predict_next_price(
            features_df,
            current_price_override=live_current_price,
            latest_volatility=latest_volatility
        )
        
        if prediction is None:
            return None

        # Generate signal using adaptive threshold if requested
        base_signal = self.generate_signal(prediction, threshold, volatility=latest_volatility)
        
        # Enhance signal using technical context and support/resistance
        enhancer = EnhancedPredictor(self.company_name, self.ticker, self)
        enhanced_signal = enhancer.refine_signal(prediction, threshold, features_df)
        enhanced_signal['recommendation'] = RECOMMENDATIONS.get(enhanced_signal['signal'], "No recommendation")
        enhanced_signal['signal_source'] = 'enhanced'
        enhanced_signal['base_signal'] = base_signal
        
        # Assess risk
        current_price = prediction['current_price']
        risk = self.assess_risk(features_df, current_price)
        
        # Get latest indicators
        engineer = FeatureEngineer(features_df)
        indicators = engineer.get_latest_indicators()
        
        # Calculate price targets using enhanced logic
        price_targets = enhancer.calculate_price_targets(prediction, features_df)
        
        # Compile analysis
        full_analysis = {
            'prediction': prediction,
            'signal': enhanced_signal,
            'base_signal': base_signal,
            'targets': price_targets,
            'risk': risk,
            'indicators': indicators,
            'market_data': live_data,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Add to history
        self._add_to_history(full_analysis)
        
        return full_analysis
    
    def _add_to_history(self, analysis):
        """
        Add prediction to history.
        
        Parameters:
        -----------
        analysis : dict
            Complete analysis
        """
        self.prediction_history.append(analysis)
        
        # Keep only last 100 predictions
        if len(self.prediction_history) > 100:
            self.prediction_history = self.prediction_history[-100:]
    
    def get_prediction_history(self, limit=10):
        """
        Get recent prediction history.
        
        Parameters:
        -----------
        limit : int
            Number of recent predictions to return
        
        Returns:
        --------
        list : Recent predictions
        """
        return self.prediction_history[-limit:]
    
    def export_prediction_as_dataframe(self, limit=10):
        """
        Export prediction history as DataFrame for CSV download.
        
        Parameters:
        -----------
        limit : int
            Number of predictions to export
        
        Returns:
        --------
        pd.DataFrame : Prediction history
        """
        
        history = self.get_prediction_history(limit)
        
        rows = []
        for item in history:
            rows.append({
                'Timestamp': item['timestamp'],
                'Company': item['prediction']['company_name'],
                'Ticker': item['prediction']['ticker'],
                'Current Price': f"₹{item['prediction']['current_price']:.2f}",
                'Predicted Price': f"₹{item['prediction']['predicted_price']:.2f}",
                'Change %': f"{item['prediction']['change_percent']:.2f}%",
                'Signal': item['signal']['signal'],
                'Confidence': f"{item['signal']['confidence']:.2%}",
                'Risk Level': item['risk']['risk_level']
            })
        
        return pd.DataFrame(rows)
    
    def get_model_metrics(self):
        """
        Get model evaluation metrics.
        
        Returns:
        --------
        dict : Model performance metrics
        """
        
        if self.trainer.training_metrics is None:
            return None
        
        metrics = self.trainer.training_metrics
        
        # Return only Test metrics for AI Insights (per user request)
        return {
            'Test MAE': f"${metrics['test_mae']:.2f}",
            'Test RMSE': f"${metrics['test_rmse']:.2f}",
            'Test R²': f"{metrics['test_r2']:.4f}",
        }
    
    def get_feature_importance(self, top_n=5):
        """
        Get top N most important features.
        
        Parameters:
        -----------
        top_n : int
            Number of top features to return
        
        Returns:
        --------
        dict : Feature importance
        """
        
        importance = self.trainer.get_feature_importance()
        
        if importance is None:
            return None
        
        return dict(list(importance.items())[:top_n])


# ==================== EXAMPLE USAGE ====================

def example_usage():
    """Example of how to use ModelPredictor"""
    
    from backend.utils.data_fetcher import DataFetcher
    
    # Initialize
    fetcher = DataFetcher()
    predictor = ModelPredictor('Infosys Limited', 'INFY.NS')
    
    # Fetch data
    print("Fetching data...")
    data = fetcher.fetch_historical_data('INFY.NS', days=365)
    
    if data is not None:
        # Prepare features
        engineer = FeatureEngineer(data)
        features_df = engineer.prepare_features()
        
        # Train model (in real app, would load pre-trained model)
        print("Training model...")
        X, y = predictor.trainer.prepare_training_data(features_df)
        predictor.trainer.train_model(X, y)
        
        # Get live data
        print("Fetching live data...")
        live_data = fetcher.fetch_live_data('INFY.NS')
        
        # Make analysis
        print("Making analysis...")
        analysis = predictor.get_full_analysis(features_df, live_data, threshold=0.02)
        
        if analysis:
            print(f"\nPrediction: {analysis['prediction']['predicted_price']:.2f}")
            print(f"Signal: {analysis['signal']['signal']}")
            print(f"Risk: {analysis['risk']['risk_level']}")
            print(f"Confidence: {analysis['signal']['confidence']:.2%}")


if __name__ == "__main__":
    example_usage()
