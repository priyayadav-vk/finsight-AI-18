from utils.data_fetcher import DataFetcher
import json

if __name__ == '__main__':
    f = DataFetcher()
    status = f.check_yahoo_status()
    print(json.dumps(status))
