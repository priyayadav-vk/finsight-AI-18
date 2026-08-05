from backend.utils.model_checker import ModelChecker
from backend.utils.model_trainer import ModelTrainer
import joblib, os, csv

checker = ModelChecker()
models_dir = checker.models_dir
report_file = os.path.join(models_dir, 'validation_report.csv')

rows = []

for ticker_clean in sorted(checker.available_tickers):
    ticker_dot = ticker_clean.replace('_', '.')
    model_file = os.path.join(models_dir, f"{ticker_clean}_model.pkl")
    scaler_file = os.path.join(models_dir, f"{ticker_clean}_scaler.pkl")
    metadata_file = os.path.join(models_dir, f"{ticker_clean}_metadata.pkl")

    note = ''
    metadata = None
    if os.path.exists(metadata_file):
        try:
            metadata = joblib.load(metadata_file)
        except Exception as e:
            note = f'metadata_load_error: {e}'

    company_name = metadata.get('company_name') if metadata and isinstance(metadata, dict) else ticker_dot

    trainer = ModelTrainer(company_name, ticker_dot)
    loaded = trainer.load_model()
    stale = getattr(trainer, 'model_is_stale', False)
    metrics = trainer.training_metrics or (metadata.get('metrics') if metadata and isinstance(metadata, dict) else None)
    train_r2 = metrics.get('train_r2') if metrics else ''
    test_r2 = metrics.get('test_r2') if metrics else ''

    # Check feature schema
    expected_features = list(trainer.feature_columns)
    saved_features = metadata.get('feature_columns') if metadata and isinstance(metadata, dict) else None
    schema_ok = (saved_features is None) or (list(saved_features) == expected_features)
    if not schema_ok:
        note += ' feature_schema_mismatch;'

    rows.append({
        'ticker': ticker_dot,
        'ticker_clean': ticker_clean,
        'company_name': company_name,
        'model_file': model_file if os.path.exists(model_file) else '',
        'scaler_file': scaler_file if os.path.exists(scaler_file) else '',
        'metadata_file': metadata_file if os.path.exists(metadata_file) else '',
        'loaded': loaded,
        'stale': stale,
        'train_r2': train_r2,
        'test_r2': test_r2,
        'schema_ok': schema_ok,
        'note': note
    })

# Write CSV
with open(report_file, 'w', newline='', encoding='utf-8') as fh:
    writer = csv.DictWriter(fh, fieldnames=['ticker','ticker_clean','company_name','model_file','scaler_file','metadata_file','loaded','stale','train_r2','test_r2','schema_ok','note'])
    writer.writeheader()
    for r in rows:
        writer.writerow(r)

print('Validation complete. Report saved to:', report_file)
for r in rows:
    print(r['ticker'], 'loaded=', r['loaded'], 'stale=', r['stale'], 'test_r2=', r['test_r2'], 'note=', r['note'])
