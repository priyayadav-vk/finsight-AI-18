"""
Data Fetcher Module
Handles downloading live stock data from Yahoo Finance
Includes demo mode fallback for network issues
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
import io
from contextlib import redirect_stdout, redirect_stderr
warnings.filterwarnings('ignore')

from config import INDIAN_COMPANIES, HISTORICAL_DAYS, DATA_PATH, is_blocked_company_name
import os


class DataFetcher:
    """
    Fetches real-time and historical stock data from Yahoo Finance.
    
    Features:
    - Download historical data for training
    - Fetch live market data
    - Handle missing data gracefully
    - Cache data locally
    """
    
    def __init__(self):
        """Initialize the DataFetcher"""
        self.data_path = DATA_PATH
        os.makedirs(self.data_path, exist_ok=True)

    def check_yahoo_status(self, test_ticker=None):
        """
        Quick check to verify Yahoo Finance service is responding.

        Returns a dict with keys: 'available' (bool), 'message' (str), 'last_checked' (ISO datetime)
        """
        try:
            # Pick a sensible default test ticker from known companies
            if test_ticker is None:
                test_ticker = None
                for info in INDIAN_COMPANIES.values():
                    nse = info.get('NSE')
                    if nse:
                        test_ticker = nse
                        break
                if test_ticker is None:
                    test_ticker = 'RELIANCE.NS'

            yahoo_ticker = self._resolve_ticker_for_yahoo(test_ticker)
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                stock = yf.Ticker(yahoo_ticker)
                data = stock.history(period='2d')

            if data is None or data.empty:
                return {
                    'available': False,
                    'message': f'Yahoo returned no data for test ticker {test_ticker}',
                    'last_checked': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }

            return {
                'available': True,
                'message': f'Yahoo responded for test ticker {test_ticker}',
                'last_checked': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

        except Exception as e:
            return {
                'available': False,
                'message': f'Error contacting Yahoo: {str(e)}',
                'last_checked': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

    def _resolve_ticker_for_yahoo(self, ticker):
        """
        Normalize market symbols so Yahoo Finance can resolve them reliably.
        For Indian BSE codes such as 500002.BO, map them to the matching NSE
        ticker like 3MINDIA.NS when available.
        """
        normalized_ticker = str(ticker).strip()

        if normalized_ticker.endswith('.BO'):
            for company_name, tickers in INDIAN_COMPANIES.items():
                if tickers.get('BSE', '').upper() == normalized_ticker.upper():
                    nse_ticker = tickers.get('NSE')
                    if nse_ticker:
                        return nse_ticker

        return normalized_ticker
    
    def fetch_live_data(self, ticker):
        """
        Fetch the latest live data for a stock.
        
        Parameters:
        -----------
        ticker : str
            Stock ticker symbol (e.g., 'RELIANCE.NS')
        
        Returns:
        --------
        dict : Contains current price, open, high, low, close, volume, etc.
        """
        try:
            yahoo_ticker = self._resolve_ticker_for_yahoo(ticker)

            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                stock = yf.Ticker(yahoo_ticker)
                
                # Get historical data (last 5 days to get today's data)
                data = stock.history(period='5d')
            
            if data.empty:
                raise Exception(f"No data returned for {ticker}")
            
            # Get the latest row (today's or latest available data)
            latest = data.iloc[-1]
            
            # Get additional info
            info = stock.info if hasattr(stock, 'info') else {}
            
            # Get market status (Open/Closed)
            now = datetime.now()
            market_open_time = now.replace(hour=9, minute=15, second=0)
            market_close_time = now.replace(hour=15, minute=30, second=0)
            
            if now.weekday() < 5:  # Weekday (Monday=0 to Friday=4)
                if market_open_time <= now <= market_close_time:
                    market_status = "[OPEN]"
                else:
                    market_status = "[CLOSED]"
            else:
                market_status = "[CLOSED] (Weekend)"
            
            live_data = {
                'ticker': ticker,
                'company_name': info.get('longName', ticker),
                'current_price': latest['Close'],
                'open_price': latest['Open'],
                'high_price': latest['High'],
                'low_price': latest['Low'],
                'previous_close': data.iloc[-2]['Close'] if len(data) > 1 else latest['Close'],
                'volume': latest['Volume'],
                'market_status': market_status,
                'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'date': latest.name.strftime("%Y-%m-%d")
            }
            
            return live_data
        
        except Exception as e:
            # Fallback to demo data
            return self._get_demo_data(ticker)
    
    def fetch_historical_data(self, ticker, days=HISTORICAL_DAYS):
        """
        Download historical data for machine learning training.
        
        Parameters:
        -----------
        ticker : str
            Stock ticker symbol
        days : int
            Number of historical days to fetch (default: 750 days ~3 years)
        
        Returns:
        --------
        pd.DataFrame : Historical OHLCV data
        """
        try:
            # Load cached historical data first to avoid repeated Yahoo requests
            cache_key = ticker.replace('.', '_')
            cached = self.load_cached_data(cache_key, cache_type='historical')
            if cached is not None and not cached.empty:
                return cached

            # Calculate start date
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            yahoo_ticker = self._resolve_ticker_for_yahoo(ticker)

            # Download data from Yahoo Finance
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                data = yf.download(
                    yahoo_ticker,
                    start=start_date,
                    end=end_date,
                    interval='1d',
                    progress=False,
                    auto_adjust=False,
                    actions=False
                )
            
            if data.empty:
                demo_data = self._generate_demo_historical_data(ticker)
                self.cache_data(cache_key, demo_data, cache_type='historical')
                return demo_data
            
            # Keep only the required OHLCV columns, regardless of Yahoo's extra columns
            required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            missing_columns = [col for col in required_columns if col not in data.columns]
            if missing_columns:
                raise ValueError(f"Missing required columns for {ticker}: {missing_columns}")
            
            data = data[required_columns].copy()
            
            # Reset index to make date a column
            data.reset_index(inplace=True)
            
            # Rename 'Date' column
            data.rename(columns={'Date': 'Date'}, inplace=True)
            
            # Remove rows with missing data
            data = data.dropna()
            
            # Ensure date column is datetime
            data['Date'] = pd.to_datetime(data['Date'])
            
            # Convert OHLCV columns to proper numeric types
            data['Open'] = pd.to_numeric(data['Open'], errors='coerce').astype(float)
            data['High'] = pd.to_numeric(data['High'], errors='coerce').astype(float)
            data['Low'] = pd.to_numeric(data['Low'], errors='coerce').astype(float)
            data['Close'] = pd.to_numeric(data['Close'], errors='coerce').astype(float)
            data['Volume'] = pd.to_numeric(data['Volume'], errors='coerce').astype(int)
            
            # Remove any rows with NaN after conversion
            data = data.dropna()

            self.cache_data(cache_key, data, cache_type='historical')
            
            return data
        
        except Exception as e:
            # Try demo mode as fallback
            demo_data = self._generate_demo_historical_data(ticker)
            self.cache_data(cache_key, demo_data, cache_type='historical')
            return demo_data
    
    def _get_demo_data(self, ticker):
        """
        Generate realistic demo market data for testing.
        This is a fallback when live Yahoo Finance data is unavailable.
        
        Parameters:
        -----------
        ticker : str
            Stock ticker symbol
        
        Returns:
        --------
        dict : Mock live market data
        """
        # Look up company name from config
        company_name = None
        for name, tickers in INDIAN_COMPANIES.items():
            if tickers.get('NSE') == ticker or tickers.get('BSE') == ticker:
                company_name = name
                break
        
        if not company_name:
            company_name = ticker
        
        # Generate realistic stock prices (base price varies by company)
        base_prices = {
            'TCS': 3500, 'INFY': 1500, 'RELIANCE': 2500, 'HDFC': 2700,
            'ICICI': 950, 'SBIN': 550, 'MARUTI': 9000, 'BAJAJ': 8500,
            'WIPRO': 400, 'HCL': 1800
        }
        
        # Find a base price for this ticker
        base_price = base_prices.get(ticker.split('.')[0], 2000)
        
        # Add realistic random variation
        np.random.seed(hash(ticker) % 2**32)
        variation = np.random.normal(0, 50)
        current_price = base_price + variation
        
        open_price = current_price + np.random.uniform(-100, 100)
        high_price = max(current_price, open_price) + np.random.uniform(0, 150)
        low_price = min(current_price, open_price) - np.random.uniform(0, 150)
        previous_close = current_price + np.random.uniform(-200, 200)
        volume = np.random.randint(100000, 10000000)
        
        now = datetime.now()
        market_open_time = now.replace(hour=9, minute=15, second=0)
        market_close_time = now.replace(hour=15, minute=30, second=0)
        
        if now.weekday() < 5 and market_open_time <= now <= market_close_time:
            market_status = "[OPEN] (Demo)"
        else:
            market_status = "[CLOSED] (Demo)"
        
        return {
            'ticker': ticker,
            'company_name': company_name,
            'current_price': round(current_price, 2),
            'open_price': round(open_price, 2),
            'high_price': round(high_price, 2),
            'low_price': round(low_price, 2),
            'previous_close': round(previous_close, 2),
            'volume': int(volume),
            'market_status': market_status,
            'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'date': datetime.now().strftime("%Y-%m-%d"),
            'is_demo': True
        }
    
    def _generate_demo_historical_data(self, ticker):
        """
        Generate realistic demo historical data for model training.
        
        Parameters:
        -----------
        ticker : str
            Stock ticker symbol
        
        Returns:
        --------
        pd.DataFrame : Mock historical OHLCV data (365 days)
        """
        dates = pd.date_range(end=datetime.now(), periods=365, freq='D')
        
        # Generate realistic price path using random walk
        base_price = 2000
        np.random.seed(hash(ticker) % 2**32)
        returns = np.random.normal(0.0005, 0.02, 365)
        prices = base_price * np.exp(np.cumsum(returns))
        
        data = pd.DataFrame({
            'Date': dates,
            'Open': (prices * (1 + np.random.uniform(-0.01, 0.01, 365))).astype(float),
            'High': (prices * (1 + np.random.uniform(0, 0.02, 365))).astype(float),
            'Low': (prices * (1 + np.random.uniform(-0.02, 0, 365))).astype(float),
            'Close': prices.astype(float),
            'Volume': np.random.randint(1000000, 50000000, 365).astype(int)
        })
        
        # Ensure High >= Close and Low <= Close
        data['High'] = data[['Open', 'High', 'Close']].max(axis=1) * 1.001
        data['Low'] = data[['Open', 'Low', 'Close']].min(axis=1) * 0.999
        
        # Ensure proper data types
        data['Date'] = pd.to_datetime(data['Date'])
        data['Open'] = data['Open'].astype(float)
        data['High'] = data['High'].astype(float)
        data['Low'] = data['Low'].astype(float)
        data['Close'] = data['Close'].astype(float)
        data['Volume'] = data['Volume'].astype(int)
        
        return data
    
    def get_company_ticker(self, company_name):
        """
        Get NSE ticker for a company.
        
        Parameters:
        -----------
        company_name : str
            Company name from config
        
        Returns:
        --------
        dict : {'NSE': ticker, 'BSE': ticker} or None
        """
        if company_name in INDIAN_COMPANIES:
            return INDIAN_COMPANIES[company_name]
        return None
    
    def get_all_companies_list(self):
        """
        Get list of all companies.
        
        Returns:
        --------
        list : Sorted list of company names
        """
        return sorted(list(INDIAN_COMPANIES.keys()))

    def get_supported_companies(self, force_refresh=False, universe='indian'):
        """
        Return a mapping of company name -> ticker info for companies
        that are known to be supported by Yahoo (loaded from a saved
        `live_supported_companies.json`) or from the verified catalog.

        If `force_refresh` is True and the live-supported file is missing,
        attempt to fall back to the verified `yahoo_live_companies.json`.
        """
        try:
            # Choose file paths based on requested universe
            if universe == 'foreign':
                live_file = os.path.join(self.data_path, 'foreign_live_companies.json')
                verified_file = os.path.join(self.data_path, 'foreign_yahoo_live_companies.json')
            else:
                live_file = os.path.join(self.data_path, 'live_supported_companies.json')
                verified_file = os.path.join(self.data_path, 'yahoo_live_companies.json')

            # Prefer the explicit live_supported list when present
            if os.path.exists(live_file) and not force_refresh:
                try:
                    import json
                    with open(live_file, 'r', encoding='utf-8') as fh:
                        names = json.load(fh)
                    if isinstance(names, list) and names:
                        mapping = {}
                        if universe == 'foreign':
                            # foreign files are expected to store dict name->ticker or list of tickers
                            # support both shapes
                            if isinstance(names, dict):
                                for name, tick in names.items():
                                    if isinstance(tick, str) and not is_blocked_company_name(name):
                                        mapping[name] = {'NSE': tick}
                            else:
                                for entry in names:
                                    # entry may be dict or str
                                    if isinstance(entry, dict):
                                        for name, tick in entry.items():
                                            if not is_blocked_company_name(name):
                                                mapping[name] = {'NSE': tick}
                                    elif isinstance(entry, str) and not is_blocked_company_name(entry):
                                        mapping[entry] = {'NSE': entry}
                        else:
                            mapping = {name: INDIAN_COMPANIES[name] for name in names if name in INDIAN_COMPANIES and not is_blocked_company_name(name)}
                        return mapping
                except Exception:
                    pass

            # If forced or no live file, try the verified yahoo catalog
            if os.path.exists(verified_file):
                try:
                    import json
                    with open(verified_file, 'r', encoding='utf-8') as fh:
                        raw = json.load(fh)
                    mapping = {}
                    if isinstance(raw, dict):
                        for name, tick_info in raw.items():
                            if is_blocked_company_name(name):
                                continue
                            # Normalize tick_info into the expected structure
                            if universe == 'foreign':
                                # foreign verified catalog may map name->ticker
                                if isinstance(tick_info, str):
                                    mapping[name] = {'NSE': tick_info}
                                elif isinstance(tick_info, dict):
                                    t = tick_info.get('ticker') or tick_info.get('TICKER') or tick_info.get('NSE')
                                    if t:
                                        mapping[name] = {'NSE': t}
                            else:
                                n = {
                                    'NSE': tick_info.get('NSE') or tick_info.get('nse'),
                                    'BSE': tick_info.get('BSE') or tick_info.get('bse') or '999999999.BO',
                                    'sector': tick_info.get('sector', 'General')
                                }
                                if n['NSE']:
                                    mapping[name] = n
                    if mapping:
                        return mapping
                except Exception:
                    pass

            # Nothing found — return None so callers can fall back to default registry
            return None
        except Exception:
            return None
    
    def fetch_all_live_data(self):
        """
        Fetch live data for all companies (useful for dashboard).
        
        Returns:
        --------
        dict : Company-wise live data
        """
        live_data = {}
        companies = self.get_all_companies_list()
        
        for company in companies:
            ticker_info = self.get_company_ticker(company)
            if ticker_info:
                ticker = ticker_info['NSE']
                data = self.fetch_live_data(ticker)
                if data:
                    live_data[company] = data
        
        return live_data
    
    def validate_data(self, data):
        """
        Validate if data is sufficient for analysis.
        
        Parameters:
        -----------
        data : pd.DataFrame
            Historical data
        
        Returns:
        --------
        bool : True if data is valid
        """
        if data is None or data.empty:
            return False
        
        if len(data) < 50:
            return False
        
        if data.isnull().sum().sum() > 0:
            return False
        
        return True
    
    def cache_data(self, ticker, data, cache_type='historical'):
        """
        Cache data locally to avoid repeated API calls.
        
        Parameters:
        -----------
        ticker : str
            Stock ticker
        data : pd.DataFrame
            Data to cache
        cache_type : str
            Type of cache ('historical' or 'live')
        """
        try:
            cache_file = f"{self.data_path}{ticker.replace('.', '_')}_{cache_type}.csv"
            data.to_csv(cache_file, index=False)
        except Exception:
            pass
    
    def load_cached_data(self, ticker, cache_type='historical'):
        """
        Load cached data from local storage.
        
        Parameters:
        -----------
        ticker : str
            Stock ticker
        cache_type : str
            Type of cache ('historical' or 'live')
        
        Returns:
        --------
        pd.DataFrame or None
        """
        try:
            cache_file = f"{self.data_path}{ticker.replace('.', '_')}_{cache_type}.csv"
            if os.path.exists(cache_file):
                return pd.read_csv(cache_file)
        except Exception as e:
            print(f"Error loading cached data: {str(e)}")
        
        return None


# ==================== EXAMPLE USAGE ====================

def example_usage():
    """Example of how to use DataFetcher"""
    
    fetcher = DataFetcher()
    
    # Get company list
    companies = fetcher.get_all_companies_list()
    print(f"Total companies available: {len(companies)}")
    print(f"First 5 companies: {companies[:5]}")
    
    # Example: Fetch live data for Reliance
    print("\n--- Fetching Live Data ---")
    live_data = fetcher.fetch_live_data('RELIANCE.NS')
    if live_data:
        print(f"Company: {live_data['company_name']}")
        print(f"Current Price: ₹{live_data['current_price']:.2f}")
        print(f"Market Status: {live_data['market_status']}")
    
    # Example: Fetch historical data
    print("\n--- Fetching Historical Data ---")
    hist_data = fetcher.fetch_historical_data('INFY.NS', days=100)
    if hist_data is not None:
        print(f"Data shape: {hist_data.shape}")
        print(f"Date range: {hist_data['Date'].min()} to {hist_data['Date'].max()}")
        print(hist_data.head())


if __name__ == "__main__":
    example_usage()
