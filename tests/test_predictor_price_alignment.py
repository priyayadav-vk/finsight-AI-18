from pages.prediction import select_display_prediction


def test_select_display_prediction_prefers_analysis_payload():
    analysis = {"prediction": {"current_price": 1000.0, "predicted_price": 1010.0}}
    fallback_prediction = {"current_price": 100.0, "predicted_price": 100.5}

    selected = select_display_prediction(analysis, fallback_prediction)

    assert selected["current_price"] == 1000.0
    assert selected["predicted_price"] == 1010.0
