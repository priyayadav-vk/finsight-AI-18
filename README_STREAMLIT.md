# Deploying FinSightAI to Streamlit Cloud

This repository is organized for Streamlit deployment with the application entrypoint at `app.py`.

## What changed for Streamlit Cloud
- Large pre-built model artifacts have been moved to `backend/large_models/` and are ignored by git.
- The app now supports safe Streamlit Cloud mode with `STREAMLIT_CLOUD=1`.
- If `MODEL_BASE_URL` is provided, the app will attempt to download missing model files at runtime.
- If no model files are available, the Prediction page will fall back to a lightweight demo heuristic.

## Recommended settings
1. Set the Streamlit app file to `app.py`.
2. Use the included `requirements.txt`.
3. In Streamlit Cloud secrets or environment variables, set:
   - `STREAMLIT_CLOUD=1`
   - `MODEL_BASE_URL=https://example.com/path/to/model/artifacts`

If `MODEL_BASE_URL` is configured, the app will try to download:
- `<MODEL_BASE_URL>/<ticker>_model.pkl`
- `<MODEL_BASE_URL>/<ticker>_scaler.pkl`
- `<MODEL_BASE_URL>/<ticker>_metadata.pkl`

## What to expect
- If model artifacts are available, the app loads them and runs full predictions.
- If model artifacts cannot be downloaded or are absent, the Prediction page still works in demo mode and shows a safe heuristic forecast.

## Local development
For local development, run:

```bash
streamlit run app.py
```

If you want the app to use locally stored models, place them in `backend/large_models/` or configure `MODEL_BASE_URL`.

## Notes
- The repository should remain lightweight for Streamlit Cloud.
- The app no longer performs heavy automatic training on Streamlit Cloud.
