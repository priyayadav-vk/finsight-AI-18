"""
Diagnostic Tool - Check which stocks have Yahoo Finance data available
Helps identify stocks that will fall back to demo/synthetic data
"""

import yfinance as yf
import pandas as pd
from config import INDIAN_COMPANIES
import io
from contextlib import redirect_stdout, redirect_stderr
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def test_ticker_availability():
    """Test which tickers have data available on Yahoo Finance"""
    
    results = {
        'available': [],
        'unavailable': [],
        'errors': []
    }
    
    logger.info("\n" + "="*70)
    logger.info("DIAGNOSTIC REPORT: Yahoo Finance Data Availability")
    logger.info("="*70 + "\n")
    
    companies_list = sorted(INDIAN_COMPANIES.items())
    total = len(companies_list)
    
    for idx, (company_name, tickers) in enumerate(companies_list, 1):
        nse_ticker = tickers.get('NSE')
        bse_ticker = tickers.get('BSE')
        
        # Try NSE first
        status = "❌"
        data_available = False
        reason = ""
        
        try:
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                stock = yf.Ticker(nse_ticker)
                data = stock.history(period='5d')
            
            if not data.empty:
                data_available = True
                status = "✓"
                reason = f"NSE ({nse_ticker})"
                results['available'].append((company_name, nse_ticker, "NSE"))
            else:
                # Try BSE
                with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                    stock = yf.Ticker(bse_ticker)
                    data = stock.history(period='5d')
                
                if not data.empty:
                    data_available = True
                    status = "✓"
                    reason = f"BSE ({bse_ticker})"
                    results['available'].append((company_name, bse_ticker, "BSE"))
                else:
                    reason = "No data on either NSE or BSE"
                    results['unavailable'].append((company_name, nse_ticker, "No data found"))
        
        except Exception as e:
            reason = f"Error: {str(e)[:50]}"
            results['errors'].append((company_name, nse_ticker, str(e)[:100]))
        
        logger.info(f"[{idx:3d}/{total}] {status} {company_name:25s} | {reason}")
    
    logger.info("\n" + "="*70)
    logger.info("SUMMARY")
    logger.info("="*70)
    logger.info(f"✓ Available on Yahoo Finance:    {len(results['available']):3d}")
    logger.info(f"❌ Unavailable (will use demo):   {len(results['unavailable']):3d}")
    logger.info(f"⚠ Errors during check:          {len(results['errors']):3d}")
    logger.info(f"📊 Total stocks tested:          {total:3d}")
    
    if results['unavailable']:
        logger.info("\n" + "-"*70)
        logger.info("STOCKS THAT WILL USE SYNTHETIC DATA:")
        logger.info("-"*70)
        for company_name, ticker, reason in sorted(results['unavailable'])[:20]:
            logger.info(f"  • {company_name:30s} ({ticker})")
        if len(results['unavailable']) > 20:
            logger.info(f"  ... and {len(results['unavailable']) - 20} more")
    
    logger.info("\n" + "="*70 + "\n")
    
    return results

def generate_data_source_report():
    """Generate a report of which stocks have real data vs synthetic"""
    
    logger.info("\nGenerating Data Source Mapping...\n")
    
    results = test_ticker_availability()
    
    # Create mapping file
    mapping = {
        'Real Data (Yahoo Finance)': [item[0] for item in results['available']],
        'Synthetic Data (Demo Mode)': [item[0] for item in results['unavailable']],
        'Errors': [item[0] for item in results['errors']]
    }
    
    # Save to CSV
    df_data = []
    for company_name, tickers in INDIAN_COMPANIES.items():
        source = 'Real Data'
        if any(item[0] == company_name for item in results['unavailable']):
            source = 'Synthetic Data'
        elif any(item[0] == company_name for item in results['errors']):
            source = 'Error'
        
        df_data.append({
            'Company': company_name,
            'NSE': tickers.get('NSE'),
            'BSE': tickers.get('BSE'),
            'Data Source': source
        })
    
    df = pd.DataFrame(df_data)
    df = df.sort_values('Data Source')
    
    # Save report
    report_file = 'data_source_report.csv'
    df.to_csv(report_file, index=False)
    logger.info(f"✓ Report saved to: {report_file}\n")
    
    return df

if __name__ == "__main__":
    results = test_ticker_availability()
    report_df = generate_data_source_report()
    
    print("\nData Source Report:")
    print(report_df.to_string(index=False))
