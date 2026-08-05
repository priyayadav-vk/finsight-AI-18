"""
Model Checker Module
Checks which models are available and validates company/exchange combinations
"""

import os
from pathlib import Path


class ModelChecker:
    """Check available trained models and validate company selections"""
    
    def __init__(self, models_dir=None):
        """
        Initialize ModelChecker.
        
        Parameters:
        -----------
        models_dir : str, optional
            Path to models directory (absolute or relative to project root)
            If None, will auto-detect project root
        """
        if models_dir is None:
            project_root = Path(__file__).resolve().parent.parent
            models_dir = project_root / "models"
        else:
            models_path = Path(models_dir).expanduser()
            if not models_path.is_absolute():
                project_root = Path(__file__).resolve().parent.parent
                models_path = project_root / models_path
            models_dir = models_path

        self.models_dir = Path(models_dir).resolve()
        self.available_tickers = self._get_available_tickers()
    
    def _get_available_tickers(self):
        """Get list of all available model tickers"""
        tickers = set()
        
        if not self.models_dir.exists():
            return tickers
        
        try:
            for file in self.models_dir.glob("*_model.pkl"):
                # Extract ticker from filename (e.g., "RELIANCE_NS_model.pkl" -> "RELIANCE_NS")
                ticker = file.stem.replace("_model", "")
                tickers.add(ticker)
        except Exception as e:
            print(f"Error reading models directory: {e}")
        
        return tickers
    
    def has_model(self, ticker):
        """
        Check if a trained model exists for a ticker.
        
        Parameters:
        -----------
        ticker : str
            Stock ticker (e.g., "500180.BO" or "RELIANCE.NS")
        
        Returns:
        --------
        bool : True if model exists
        """
        if not ticker:
            return False
        
        # Normalize ticker: convert dot to underscore
        # "500180.BO" -> "500180_BO", "RELIANCE.NS" -> "RELIANCE_NS"
        normalized_ticker = ticker.replace(".", "_")
        return normalized_ticker in self.available_tickers
    
    def get_available_exchanges(self, company_name, company_info):
        """
        Get exchanges that are actually usable for this company.

        Show BSE only when the company is registered on BSE. Otherwise, show NSE.
        Only return an exchange if a trained model exists for that ticker.
        """
        available = []

        if company_info.get('NSE') and self.has_model(company_info.get('NSE')):
            available.append('NSE')

        if company_info.get('BSE') and self.has_model(company_info.get('BSE')):
            available.append('BSE')

        return available
    
    def get_companies_with_models(self, all_companies):
        """
        Filter companies to those that are usable in the app.

        A company is considered usable only if at least one registered exchange
        has a trained model.
        """
        filtered = {}

        for company_name, company_info in all_companies.items():
            exchanges = self.get_available_exchanges(company_name, company_info)
            if exchanges:
                filtered[company_name] = company_info

        return filtered
