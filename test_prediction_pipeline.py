from config import INDIAN_COMPANIES
from utils.data_fetcher import DataFetcher
from utils.features import FeatureEngineer
from utils.model_checker import ModelChecker
from utils.model_predictor import ModelPredictor


def main():
    checker = ModelChecker()
    companies = checker.get_companies_with_models(INDIAN_COMPANIES)
    print(f"Checking {len(companies)} prediction-ready companies...")

    failures = []
    for company_name, company_info in sorted(companies.items()):
        for exchange in ("NSE", "BSE"):
            ticker = company_info.get(exchange)
            if not ticker or not checker.has_model(ticker):
                continue

            try:
                fetcher = DataFetcher()
                historical = fetcher.fetch_historical_data(ticker, days=365)
                features = FeatureEngineer(historical).prepare_features()
                predictor = ModelPredictor(company_name, ticker)

                if not predictor.load_model():
                    print(f"SKIP: {company_name} [{exchange}] -> {ticker} (no trained model available)")
                    continue

                result = predictor.predict_next_price(features)
                if result is None or result.get("predicted_price") is None:
                    failures.append((company_name, exchange, "prediction_failed"))
                    continue

                analysis = predictor.get_full_analysis(features, {"current_price": result["current_price"]}, 0.02)
                if not analysis or not analysis.get("signal"):
                    failures.append((company_name, exchange, "analysis_failed"))
                    continue

                print(f"OK: {company_name} [{exchange}] -> {ticker}")
            except Exception as exc:  # pragma: no cover - regression guard
                failures.append((company_name, exchange, str(exc)))

    if failures:
        print("FAILED:")
        for failure in failures[:10]:
            print(f" - {failure}")
        raise SystemExit(1)

    print("All prediction-ready companies completed successfully.")


if __name__ == "__main__":
    main()
