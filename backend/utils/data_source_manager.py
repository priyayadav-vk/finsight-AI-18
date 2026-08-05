"""
Data Source Manager - Intelligent fallback strategy
Tries multiple data sources in order of preference
"""

import pandas as pd
import os
from pathlib import Path
import logging

from backend.config import DATA_PATH

logger = logging.getLogger(__name__)

class DataSourceManager:
    """Manages data fetching with intelligent fallback strategy"""
    
    @staticmethod
    def get_data_with_fallback(ticker, fetcher, data_type='live'):
        """
        Fetch data with intelligent fallback strategy:
        1. Try Yahoo Finance (real-time)
        2. Use cached data if available
        3. Use local CSV files
        4. Generate synthetic data as last resort
        
        Parameters:
        -----------
        ticker : str
            Stock ticker
        fetcher : DataFetcher
            DataFetcher instance
        data_type : str
            'live' or 'historical'
        
        Returns:
        --------
        dict/DataFrame : Data with source information
        """
        result = None
        source = None
        
        try:
            if data_type == 'live':
                result = fetcher.fetch_live_data(ticker)
                if result and not result.get('is_demo'):
                    source = 'Yahoo Finance (Live)'
                    logger.info(f"✓ {ticker}: Using real-time data from Yahoo Finance")
                    return result, source
            
            # Try cached data
            cache_file = _find_cache_file(ticker)
            if cache_file:
                logger.info(f"✓ {ticker}: Using cached data")
                return _load_cache(cache_file), 'Cached Data'
            
            # Try local CSV files
            csv_file = _find_local_csv(ticker)
            if csv_file:
                logger.info(f"✓ {ticker}: Using local CSV file")
                return _load_csv(csv_file), 'Local CSV'
            
            # Last resort: synthetic data
            logger.warning(f"⚠ {ticker}: All sources unavailable, using synthetic data")
            if data_type == 'live':
                return fetcher._get_demo_data(ticker, is_fallback=True), 'Synthetic Data (Fallback)'
            else:
                return fetcher._generate_demo_historical_data(ticker), 'Synthetic Data (Fallback)'
        
        except Exception as e:
            logger.error(f"✗ {ticker}: Error in fallback chain: {str(e)}")
            if data_type == 'live':
                return fetcher._get_demo_data(ticker, is_fallback=True), 'Synthetic Data (Error)'
            else:
                return fetcher._generate_demo_historical_data(ticker), 'Synthetic Data (Error)'

def _find_cache_file(ticker):
    """Find cached data file for ticker (search DATA_PATH and legacy data/ folder)."""
    tkey = ticker.replace('.', '_')
    candidates = [
        os.path.join(DATA_PATH, f"{tkey}_historical.csv"),
        os.path.join(DATA_PATH, f"{tkey}_live.csv"),
        os.path.join('data', f"{tkey}_historical.csv"),
    ]

    for cache_file in candidates:
        if cache_file and os.path.exists(cache_file):
            return cache_file

    return None

def _find_local_csv(ticker):
    """Find local CSV file for ticker inside DATA_PATH or legacy data/ folder."""
    data_dir = Path(DATA_PATH)
    if not data_dir.exists():
        data_dir = Path('data')
        if not data_dir.exists():
            return None

    # Search for files matching the ticker
    for csv_file in data_dir.glob(f"*{ticker.replace('.', '_')}*.csv"):
        if 'historical' in str(csv_file) or 'live' in str(csv_file):
            return str(csv_file)

    # fallback: try any CSV that contains the ticker string
    for csv_file in data_dir.glob(f"*{ticker}*.csv"):
        if 'historical' in str(csv_file) or 'live' in str(csv_file):
            return str(csv_file)

    return None

def _load_cache(cache_file):
    """Load cached data"""
    try:
        df = pd.read_csv(cache_file)
        return df
    except Exception as e:
        logger.error(f"Error loading cache: {str(e)}")
        return None

def _load_csv(csv_file):
    """Load CSV file"""
    try:
        df = pd.read_csv(csv_file)
        return df
    except Exception as e:
        logger.error(f"Error loading CSV: {str(e)}")
        return None
