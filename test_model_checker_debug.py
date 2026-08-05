#!/usr/bin/env python
"""Debug script for ModelChecker"""

from utils.model_checker import ModelChecker
from config import INDIAN_COMPANIES

checker = ModelChecker()
print('Available tickers:', checker.available_tickers)
print()

# Test with first few companies
for company_name, company_info in list(INDIAN_COMPANIES.items())[:10]:
    exchanges = checker.get_available_exchanges(company_name, company_info)
    print(f'{company_name}:')
    print(f'  NSE: {company_info.get("NSE")} -> has_model: {checker.has_model(company_info.get("NSE"))}')
    print(f'  BSE: {company_info.get("BSE")} -> has_model: {checker.has_model(company_info.get("BSE"))}')
    print(f'  Available: {exchanges}')
    print()

# Full test
companies_with_models = checker.get_companies_with_models(INDIAN_COMPANIES)
print(f'\nTotal companies with models: {len(companies_with_models)}')
