"""
Feature Engineering Module
Calculates technical indicators for machine learning
"""

import pandas as pd
import numpy as np
from ta.momentum import RSIIndicator
from ta.trend import MACD, EMAIndicator
from ta.volatility import BollingerBands, AverageTrueRange
from backend.config import MA_PERIODS, RSI_PERIOD, MACD_FAST, MACD_SLOW, MACD_SIGNAL, BB_PERIOD, BB_STD


class FeatureEngineer:
    """
    Calculates technical indicators and prepares features for ML model.
    
    Indicators calculated:
    1. MA10 & MA20: Moving Averages (short & medium term trends)
    2. RSI: Relative Strength Index (momentum 0-100)
    3. MACD: Moving Average Convergence Divergence (trend signal)
    4. Bollinger Bands: Upper and Lower bands (support & resistance)
    5. Daily Return: Percentage change in price
    6. Volatility: Standard deviation of returns
    """
    
    def __init__(self, df):
        """
        Initialize FeatureEngineer with historical data.
        
        Parameters:
        -----------
        df : pd.DataFrame
            Historical OHLCV data with columns: Date, Open, High, Low, Close, Volume
        """
        self.df = df.copy()
        self.df = self.df.sort_values('Date').reset_index(drop=True)
        
        # Ensure proper data types
        self._ensure_numeric_types()
    
    def _ensure_numeric_types(self):
        """
        Ensure all OHLCV columns are numeric types.
        Converts string values to float if needed.
        
        Returns:
        --------
        None (modifies self.df in place)
        """
        numeric_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        
        for col in numeric_columns:
            if col in self.df.columns:
                try:
                    # Convert to numeric, coercing errors to NaN
                    self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
                except Exception as e:
                    print(f"Warning: Could not convert {col} to numeric: {e}")
        
        # Ensure Date is datetime
        if 'Date' in self.df.columns:
            self.df['Date'] = pd.to_datetime(self.df['Date'], errors='coerce')
        
        # Remove any rows with NaN in critical columns
        self.df = self.df.dropna(subset=['Close', 'Open', 'High', 'Low', 'Volume'])
    
    def calculate_moving_averages(self):
        """
        Calculate Moving Averages (MA10 and MA20).
        
        What it does:
        - MA10: Average of last 10 days closing prices (short-term trend)
        - MA20: Average of last 20 days closing prices (medium-term trend)
        
        Formula: MA = Sum of last N closing prices / N
        
        Returns:
        --------
        None (modifies self.df in place)
        """
        for period in MA_PERIODS:
            self.df[f'MA{period}'] = self.df['Close'].rolling(window=period).mean()
    
    def calculate_rsi(self):
        """
        Calculate Relative Strength Index (RSI).
        
        What it does:
        - Measures momentum on scale of 0-100
        - RSI > 70: Stock is OVERBOUGHT (potential sell signal)
        - RSI < 30: Stock is OVERSOLD (potential buy signal)
        - RSI 30-70: Neutral zone
        
        Formula:
        RSI = 100 - (100 / (1 + RS))
        RS = Average Gain / Average Loss
        
        Returns:
        --------
        None (modifies self.df in place)
        """
        rsi_indicator = RSIIndicator(
            close=self.df['Close'],
            window=RSI_PERIOD
        )
        self.df['RSI'] = rsi_indicator.rsi()
    
    def calculate_macd(self):
        """
        Calculate Moving Average Convergence Divergence (MACD).
        
        What it does:
        - MACD Line: Difference between fast (12) and slow (26) EMAs
        - Signal Line: 9-period EMA of MACD
        - Histogram: MACD - Signal Line
        
        Trading Signals:
        - When MACD > Signal: Bullish (potential BUY)
        - When MACD < Signal: Bearish (potential SELL)
        - Histogram shows strength of trend
        
        Returns:
        --------
        None (modifies self.df in place)
        """
        macd_indicator = MACD(
            close=self.df['Close'],
            window_fast=MACD_FAST,
            window_slow=MACD_SLOW,
            window_sign=MACD_SIGNAL
        )
        
        self.df['MACD'] = macd_indicator.macd()
        self.df['MACD_Signal'] = macd_indicator.macd_signal()
        self.df['MACD_Hist'] = macd_indicator.macd_diff()
    
    def calculate_bollinger_bands(self):
        """
        Calculate Bollinger Bands.
        
        What it does:
        - Upper Band: MA + (2 * Standard Deviation)
        - Lower Band: MA - (2 * Standard Deviation)
        - Middle Band: 20-period Simple Moving Average
        
        Trading Signals:
        - Price at Upper Band: Stock may be OVERBOUGHT
        - Price at Lower Band: Stock may be OVERSOLD
        - Band Width: Indicates volatility
        
        Returns:
        --------
        None (modifies self.df in place)
        """
        bb_indicator = BollingerBands(
            close=self.df['Close'],
            window=BB_PERIOD,
            window_dev=BB_STD
        )
        
        self.df['BB_High'] = bb_indicator.bollinger_hband()
        self.df['BB_Low'] = bb_indicator.bollinger_lband()
        self.df['BB_Middle'] = bb_indicator.bollinger_mavg()

    def calculate_ema(self):
        """
        Calculate exponential moving averages for trend sensitivity.
        """
        self.df['EMA10'] = EMAIndicator(close=self.df['Close'], window=10).ema_indicator()
        self.df['EMA20'] = EMAIndicator(close=self.df['Close'], window=20).ema_indicator()
        self.df['EMA50'] = EMAIndicator(close=self.df['Close'], window=50).ema_indicator()

    def calculate_atr(self):
        """
        Calculate Average True Range as a volatility feature.
        """
        atr_indicator = AverageTrueRange(
            high=self.df['High'],
            low=self.df['Low'],
            close=self.df['Close'],
            window=14
        )
        self.df['ATR'] = atr_indicator.average_true_range()

    def calculate_momentum(self):
        """
        Calculate a simple momentum feature over 10 days.
        """
        self.df['Momentum_10'] = self.df['Close'].diff(10)

    def calculate_close_open_ratio(self):
        """
        Calculate the close/open ratio for intraday strength.
        """
        self.df['Close_Open_Ratio'] = self.df['Close'] / self.df['Open']

    def calculate_daily_return(self):
        """
        Calculate the daily percentage return.
        """
        self.df['Daily_Return'] = self.df['Close'].pct_change()

    def calculate_rolling_returns(self, window):
        """
        Calculate rolling forward returns for a fixed window.
        """
        self.df[f'Return_{window}D'] = self.df['Close'].pct_change(periods=window)

    def calculate_day_of_week(self):
        """
        Add the weekday as a categorical feature.
        """
        self.df['DayOfWeek'] = self.df['Date'].dt.weekday
    
    def calculate_volume_change(self):
        """
        Calculate daily volume change percentage.
        """
        self.df['Volume_Change'] = self.df['Volume'].pct_change()
    
    def calculate_ma_features(self):
        """
        Calculate additional moving average features.
        """
        self.df['MA_Ratio'] = self.df['MA10'] / self.df['MA20']
        self.df['MA_Diff'] = self.df['MA10'] - self.df['MA20']
        self.df['EMA_Ratio'] = self.df['EMA10'] / self.df['EMA50']
    
    def calculate_bb_features(self):
        """
        Calculate Bollinger Band derived features.
        """
        self.df['BB_PctB'] = (
            self.df['Close'] - self.df['BB_Low']
        ) / (self.df['BB_High'] - self.df['BB_Low'])
        self.df['BB_Width'] = (
            self.df['BB_High'] - self.df['BB_Low']
        ) / self.df['BB_Middle']
    
    def calculate_volatility(self, window=20):
        """
        Calculate Rolling Volatility (Standard Deviation of Returns).
        
        What it does:
        - Measures price variability over time
        - High volatility = Higher risk & reward
        - Low volatility = Stable price movement
        
        Formula:
        Volatility = Std Dev of daily returns over N days
        
        Parameters:
        -----------
        window : int
            Rolling window for volatility (default: 20 days)
        
        Returns:
        --------
        None (modifies self.df in place)
        """
        self.df['Volatility'] = self.df['Daily_Return'].rolling(window=window).std()
    
    def prepare_features(self):
        """
        Calculate all technical indicators and prepare features for ML.
        
        This is the main function to call which:
        1. Calculates all technical indicators
        2. Removes NaN values
        3. Prepares data for machine learning
        
        Returns:
        --------
        pd.DataFrame : DataFrame with all features ready for ML
        """
        
        # Calculate all indicators
        self.calculate_moving_averages()
        self.calculate_rsi()
        self.calculate_macd()
        self.calculate_bollinger_bands()
        self.calculate_daily_return()
        self.calculate_volume_change()
        self.calculate_rolling_returns(5)
        self.calculate_rolling_returns(10)
        self.calculate_ema()
        self.calculate_momentum()
        self.calculate_atr()
        self.calculate_close_open_ratio()
        self.calculate_day_of_week()
        self.calculate_ma_features()
        self.calculate_bb_features()
        self.calculate_volatility()
        
        # Drop rows with NaN values (indicators need warmup period)
        self.df = self.df.dropna()
        
        # Ensure all required columns exist
        required_features = [
            'Date', 'Open', 'High', 'Low', 'Close', 'Volume',
            'MA10', 'MA20', 'EMA10', 'EMA20', 'EMA50',
            'MA_Ratio', 'MA_Diff', 'EMA_Ratio',
            'RSI', 'MACD', 'MACD_Signal', 'MACD_Hist',
            'BB_High', 'BB_Low', 'BB_Middle', 'BB_PctB', 'BB_Width',
            'Daily_Return', 'Return_5D', 'Return_10D', 'Momentum_10',
            'ATR', 'Volume_Change', 'Close_Open_Ratio', 'DayOfWeek', 'Volatility'
        ]
        
        # Select only required columns
        self.df = self.df[required_features]
        
        return self.df
    
    def get_latest_indicators(self):
        """
        Get the latest values of all indicators (for live prediction).
        
        Returns:
        --------
        dict : Latest indicator values
        """
        latest = self.df.iloc[-1]
        
        indicators = {
            'Date': latest['Date'],
            'Close': latest['Close'],
            'MA10': latest['MA10'],
            'MA20': latest['MA20'],
            'RSI': latest['RSI'],
            'MACD': latest['MACD'],
            'MACD_Signal': latest['MACD_Signal'],
            'MACD_Hist': latest['MACD_Hist'],
            'BB_High': latest['BB_High'],
            'BB_Low': latest['BB_Low'],
            'Daily_Return': latest['Daily_Return'],
            'Volatility': latest['Volatility'],
        }
        
        return indicators
    
    def get_indicator_info(self):
        """
        Return information about all indicators.
        
        Returns:
        --------
        dict : Indicator descriptions and interpretations
        """
        return {
            'MA10': {
                'description': '10-day Moving Average',
                'interpretation': 'Short-term trend indicator',
                'bullish': 'Price above MA10',
                'bearish': 'Price below MA10'
            },
            'MA20': {
                'description': '20-day Moving Average',
                'interpretation': 'Medium-term trend indicator',
                'bullish': 'Price above MA20',
                'bearish': 'Price below MA20'
            },
            'RSI': {
                'description': 'Relative Strength Index (0-100)',
                'interpretation': 'Momentum indicator',
                'bullish': 'RSI < 50 moving upward',
                'bearish': 'RSI > 50 moving downward',
                'overbought': 'RSI > 70 (potential reversal)',
                'oversold': 'RSI < 30 (potential recovery)'
            },
            'MACD': {
                'description': 'Moving Average Convergence Divergence',
                'interpretation': 'Trend and momentum indicator',
                'bullish': 'MACD > Signal Line',
                'bearish': 'MACD < Signal Line'
            },
            'Bollinger_Bands': {
                'description': 'Upper and Lower Bollinger Bands',
                'interpretation': 'Support and Resistance levels',
                'signal': 'Price touching upper band = overbought, lower band = oversold'
            },
            'Daily_Return': {
                'description': 'Percentage change in closing price',
                'interpretation': 'Daily price movement',
                'positive': 'Price increased from previous day',
                'negative': 'Price decreased from previous day'
            },
            'Volatility': {
                'description': 'Standard deviation of daily returns',
                'interpretation': 'Price stability measurement',
                'high': 'High volatility = High risk & reward',
                'low': 'Low volatility = Stable price'
            }
        }
    
    def get_dataframe(self):
        """
        Get the processed dataframe with all features.
        
        Returns:
        --------
        pd.DataFrame : Complete feature-engineered data
        """
        return self.df


# ==================== EXAMPLE USAGE ====================

def example_usage():
    """Example of how to use FeatureEngineer"""
    
    from backend.utils.data_fetcher import DataFetcher
    
    # Fetch historical data
    fetcher = DataFetcher()
    data = fetcher.fetch_historical_data('INFY.NS', days=365)
    
    if data is not None:
        print("Creating FeatureEngineer...")
        engineer = FeatureEngineer(data)
        
        print("Preparing features...")
        features_df = engineer.prepare_features()
        
        print(f"Features prepared: {features_df.shape}")
        print(f"\nFirst 5 rows:")
        print(features_df.head())
        
        print(f"\nLatest indicators:")
        latest = engineer.get_latest_indicators()
        for key, value in latest.items():
            print(f"  {key}: {value}")
        
        print(f"\nDataframe shape: {engineer.get_dataframe().shape}")
        print(f"Columns: {list(engineer.get_dataframe().columns)}")


if __name__ == "__main__":
    example_usage()
