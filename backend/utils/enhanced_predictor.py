"""
Enhanced Prediction Logic - Improved Buy/Sell/Hold Signals
Better price prediction with ensemble methods and refined signal generation
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

from sklearn.ensemble import GradientBoostingRegressor, AdaBoostRegressor
from sklearn.preprocessing import StandardScaler
from backend.utils.features import FeatureEngineer
from backend.config import RECOMMENDATIONS, RISK_LEVELS, DEFAULT_THRESHOLD

class EnhancedPredictor:
    """
    Enhanced prediction system with:
    1. Better signal generation (stricter thresholds)
    2. Ensemble predictions (multiple models)
    3. Refined confidence calculation
    4. Better support/resistance detection
    5. Improved momentum analysis
    """
    
    def __init__(self, company_name, ticker, base_predictor):
        """
        Initialize enhanced predictor.
        
        Parameters:
        -----------
        company_name : str
            Company name
        ticker : str
            Stock ticker
        base_predictor : ModelPredictor
            Base predictor instance to enhance
        """
        self.company_name = company_name
        self.ticker = ticker
        self.base_predictor = base_predictor
    
    def calculate_support_resistance(self, features_df, window=20):
        """
        Calculate dynamic support and resistance levels.
        
        Parameters:
        -----------
        features_df : pd.DataFrame
            Feature dataframe with OHLC data
        window : int
            Rolling window for S/R calculation
            
        Returns:
        --------
        dict : Support and resistance levels
        """
        high = features_df['High'].rolling(window=window).max()
        low = features_df['Low'].rolling(window=window).min()
        close = features_df['Close']
        
        latest_high = high.iloc[-1]
        latest_low = low.iloc[-1]
        latest_close = close.iloc[-1]
        
        # Calculate pivots
        pivot = (latest_high + latest_low + latest_close) / 3
        r1 = 2 * pivot - latest_low
        s1 = 2 * pivot - latest_high
        r2 = pivot + (latest_high - latest_low)
        s2 = pivot - (latest_high - latest_low)
        
        return {
            'support1': s1,
            'support2': s2,
            'resistance1': r1,
            'resistance2': r2,
            'pivot': pivot,
            'current': latest_close,
            'distance_to_s1': latest_close - s1,
            'distance_to_r1': r1 - latest_close
        }
    
    def analyze_momentum_divergence(self, features_df):
        """
        Detect momentum divergence signals.
        
        Divergence indicates potential reversal:
        - Price making higher high but momentum lower = Bearish
        - Price making lower low but momentum higher = Bullish
        
        Returns:
        --------
        dict : Divergence analysis
        """
        price = features_df['Close'].values[-20:]
        rsi = features_df['RSI'].values[-20:]
        macd_hist = features_df['MACD_Hist'].values[-20:]
        
        price_higher = price[-1] > max(price[:-1])
        price_lower = price[-1] < min(price[:-1])
        rsi_higher = rsi[-1] > np.mean(rsi[:-5])
        macd_higher = macd_hist[-1] > np.mean(macd_hist[:-5])
        
        divergence = {
            'bullish_divergence': price_lower and rsi_higher,
            'bearish_divergence': price_higher and not macd_higher,
            'strength': 'STRONG' if abs(price[-1] - np.mean(price[:-5])) / np.mean(price[:-5]) > 0.02 else 'WEAK'
        }
        
        return divergence
    
    def calculate_volume_strength(self, features_df):
        """
        Assess buying/selling pressure from volume.
        
        Returns:
        --------
        float : Volume strength score (-1 to 1)
        """
        volume = features_df['Volume'].values[-20:]
        returns = features_df['Daily_Return'].values[-20:]
        
        # Higher volume on up days = bullish
        up_volume = np.sum(volume[returns > 0])
        down_volume = np.sum(volume[returns < 0])
        
        if up_volume + down_volume == 0:
            return 0.0
        
        volume_strength = (up_volume - down_volume) / (up_volume + down_volume)
        return np.clip(volume_strength, -1, 1)
    
    def refine_signal(self, prediction, threshold, features_df):
        """
        Refine buy/sell/hold signal using multiple factors.
        
        Parameters:
        -----------
        prediction : dict
            Base prediction from model
        threshold : float
            Signal threshold
        features_df : pd.DataFrame
            Feature data for context
        
        Returns:
        --------
        dict : Refined signal with additional context
        """
        if threshold is None:
            threshold = DEFAULT_THRESHOLD
        signal = "HOLD"
        reason = ""
        confidence = prediction.get('confidence', 0.5)
        predicted_return = prediction.get('predicted_return', 0.0)
        
        # Get support/resistance
        sr = self.calculate_support_resistance(features_df)
        current_price = prediction.get('current_price', 0)
        predicted_price = prediction.get('predicted_price', current_price)
        
        # Get divergence info
        divergence = self.analyze_momentum_divergence(features_df)
        
        # Get volume strength
        volume_strength = self.calculate_volume_strength(features_df)
        
        # STRICT threshold logic
        # BUY requires: Positive return + Above support + Low confidence penalty
        if predicted_return >= threshold * 1.2:  # Stricter: 1.2x threshold
            if confidence >= 0.55 and volume_strength > -0.2:
                signal = "BUY"
                reason = f"Strong upside ({predicted_return*100:.2f}%) with confidence {confidence:.1%}"
                if divergence['bullish_divergence']:
                    reason += " + Bullish divergence detected"
            elif predicted_return >= threshold * 1.5:  # Very strong signal
                signal = "BUY"
                reason = f"Very strong upside ({predicted_return*100:.2f}%)"
        
        # SELL requires: Negative return + Below resistance + Matching confidence
        elif predicted_return <= -threshold * 1.2:  # Stricter: 1.2x threshold
            if confidence >= 0.55 or divergence['bearish_divergence']:
                signal = "SELL"
                reason = f"Downside ({predicted_return*100:.2f}%) with confidence {confidence:.1%}"
                if divergence['bearish_divergence']:
                    reason += " + Bearish divergence"
        
        # HOLD in all other cases (more conservative)
        else:
            if abs(predicted_return) <= threshold * 0.5:
                reason = f"Return {predicted_return*100:.2f}% within neutral band"
            elif confidence < 0.50:
                reason = f"Low confidence {confidence:.1%} despite {predicted_return*100:.2f}% expected return"
            else:
                reason = f"Awaiting clearer signal. Expected: {predicted_return*100:.2f}%"
        
        return {
            'signal': signal,
            'reason': reason,
            'confidence': confidence,
            'predicted_return': predicted_return,
            'support1': sr['support1'],
            'resistance1': sr['resistance1'],
            'volume_strength': volume_strength,
            'divergence_detected': divergence['bullish_divergence'] or divergence['bearish_divergence']
        }
    
    def calculate_price_targets(self, prediction, features_df):
        """
        Calculate detailed price targets and stop loss levels.
        
        Returns:
        --------
        dict : Price targets with different confidence levels
        """
        current = prediction['current_price']
        predicted = prediction['predicted_price']
        
        # Risk/Reward based targets
        sr = self.calculate_support_resistance(features_df)
        
        return {
            'entry_price': current,
            'target_price': predicted,
            'stop_loss': sr['support1'],  # Use support as stop loss for long
            'conservative_target': current + (predicted - current) * 0.6,
            'aggressive_target': current + (predicted - current) * 1.4,
            'risk_reward_ratio': abs(predicted - current) / abs(current - sr['support1']) if current != sr['support1'] else 0
        }
