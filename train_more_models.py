from utils.data_fetcher import DataFetcher
from utils.features import FeatureEngineer
from utils.model_trainer import ModelTrainer
from config import INDIAN_COMPANIES, VALIDATED_COMPANIES

# Build the training list from validated (Yahoo-available) companies.
# Include as many validated companies as available (>=50 when possible).
COMPANIES_TO_TRAIN = []
for name in VALIDATED_COMPANIES:
    info = INDIAN_COMPANIES.get(name)
    if not info:
        continue
    nse = info.get('NSE')
    if nse and isinstance(nse, str) and nse.strip():
        COMPANIES_TO_TRAIN.append((name, nse))

# If fewer than 50 validated companies, supplement with configured companies that have NSE tickers
if len(COMPANIES_TO_TRAIN) < 50:
    for name, info in INDIAN_COMPANIES.items():
        if name in VALIDATED_COMPANIES:
            continue
        nse = info.get('NSE')
        if nse and isinstance(nse, str) and nse.strip():
            COMPANIES_TO_TRAIN.append((name, nse))
        if len(COMPANIES_TO_TRAIN) >= 50:
            break

print(f"Preparing to train models for {len(COMPANIES_TO_TRAIN)} companies")


def train_company(company_name, ticker):
    fetcher = DataFetcher()
    historical = fetcher.fetch_historical_data(ticker, days=750)
    if historical is None or historical.empty:
        raise RuntimeError(f"No historical data for {company_name} ({ticker})")

    features = FeatureEngineer(historical).prepare_features()
    if features is None or features.empty:
        raise RuntimeError(f"No feature rows for {company_name} ({ticker})")

    trainer = ModelTrainer(company_name, ticker)
    X, y = trainer.prepare_training_data(features)
    if len(X) < 50:
        raise RuntimeError(f"Not enough rows to train {company_name} ({ticker})")

    trainer.train_model(X, y)
    trainer.save_model()
    print(f"Trained: {company_name} -> {ticker}")


def main():
    print("Starting batch training for additional companies...")
    for company_name, ticker in COMPANIES_TO_TRAIN:
        try:
            train_company(company_name, ticker)
        except Exception as exc:
            print(f"FAILED: {company_name} ({ticker}) -> {exc}")
    print("Finished batch training.")


if __name__ == "__main__":
    main()
