import json
from utils.data_fetcher import DataFetcher
s = DataFetcher().check_yahoo_status('3MINDIA.NS')
print(json.dumps(s, indent=2))
