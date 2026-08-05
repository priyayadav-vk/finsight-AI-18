import os
from pathlib import Path

from config import INDIAN_COMPANIES, MODEL_PATH
from utils.data_fetcher import DataFetcher
from utils.features import FeatureEngineer
from utils.model_trainer import ModelTrainer


def train_company(company_name, ticker, target_count=100):
    fetcher = DataFetcher()
    historical = fetcher.fetch_historical_data(ticker, days=365)
    if historical is None or historical.empty:
        print(f"SKIP: no historical data -> {company_name} ({ticker})")
        return False

    features = FeatureEngineer(historical).prepare_features()
    if features is None or features.empty:
        print(f"SKIP: no feature rows -> {company_name} ({ticker})")
        return False

    trainer = ModelTrainer(company_name, ticker)
    X, y = trainer.prepare_training_data(features)
    if len(X) < 50:
        print(f"SKIP: too few rows -> {company_name} ({ticker})")
        return False

    trainer.train_model(X, y)
    trainer.save_model()
    print(f"TRAINED: {company_name} -> {ticker}")
    return True


def has_model_file(ticker):
    ticker_clean = ticker.replace('.', '_')
    return os.path.exists(os.path.join(MODEL_PATH, f"{ticker_clean}_model.pkl"))


def main():
    target_count = 100
    trained = 0
    skipped = 0

    print(f"Training up to {target_count} companies from the config list...")

    for company_name, company_info in INDIAN_COMPANIES.items():
        ticker = company_info.get("NSE")
        if not ticker:
            skipped += 1
            continue
        if ticker.startswith("999999999"):
            skipped += 1
            continue
        if has_model_file(ticker):
            continue

        try:
            ok = train_company(company_name, ticker)
            if ok:
                trained += 1
                if trained >= target_count:
                    break
        except Exception as exc:
            skipped += 1
            print(f"FAILED: {company_name} ({ticker}) -> {exc}")

    print(f"Completed training. Trained: {trained}, skipped: {skipped}")


if __name__ == "__main__":
    main()
