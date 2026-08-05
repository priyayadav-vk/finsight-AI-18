from pathlib import Path

from utils.model_checker import ModelChecker


def test_get_available_exchanges_returns_registered_markets_for_dual_listing(tmp_path):
    checker = ModelChecker(models_dir=tmp_path)
    checker.available_tickers = {"RELIANCE_NS"}

    company_info = {
        "NSE": "RELIANCE.NS",
        "BSE": "500325.BO",
    }

    exchanges = checker.get_available_exchanges("Reliance Industries Limited", company_info)

    assert exchanges == ["NSE", "BSE"]
