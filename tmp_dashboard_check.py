import traceback
from config import INDIAN_COMPANIES
from utils.data_fetcher import DataFetcher

print('Starting dashboard smoke test...')
fetcher = DataFetcher()
try:
    try:
        live_supported = fetcher.get_supported_companies(force_refresh=False, universe='indian')
    except Exception as e:
        live_supported = None
    active = live_supported if live_supported else INDIAN_COMPANIES
    if isinstance(active, dict):
        companies = sorted(list(active.keys()))
    elif isinstance(active, list):
        companies = sorted(active)
        active = {name: INDIAN_COMPANIES.get(name, {}) for name in companies}
    else:
        companies = sorted(list(INDIAN_COMPANIES.keys()))
        active = INDIAN_COMPANIES

    print('Companies count:', len(companies))
    if not companies:
        raise RuntimeError('No companies available')

    selected = companies[0]
    print('Selected company:', selected)
    info = active.get(selected)
    if info is None:
        info = INDIAN_COMPANIES.get(selected)
        print('Fell back to registry')
    print('Company info keys:', list(info.keys()))

    # Prefer NSE
    ticker = info.get('NSE') or info.get('BSE')
    if not ticker:
        raise RuntimeError('No ticker for selected company')
    print('Resolved ticker:', ticker)

    print('\nFetching live data...')
    live = fetcher.fetch_live_data(ticker)
    print('Live data sample:', {k: live.get(k) for k in ['ticker','company_name','current_price','market_status']})

    print('\nFetching historical (30 days)...')
    hist = fetcher.fetch_historical_data(ticker, days=30)
    print('Historical rows:', None if hist is None else hist.shape)

    print('\nSmoke test passed')
except Exception as e:
    print('SMOKE TEST FAILED')
    traceback.print_exc()
