"""
Prepare repository for Streamlit Cloud:
- Move large model files (models*_*.pkl) into backend/large_models
- Add backend/large_models to .gitignore
- Print summary of moved files

Run: python scripts/prepare_streamlit.py
"""
import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LARGE_DIR = ROOT / "backend" / "large_models"
ROOT_MODELS_DIR = ROOT / "models"
PATTERNS = ["models*_model.pkl", "models*_scaler.pkl", "models*_metadata.pkl", "models*.pkl"]

os.makedirs(LARGE_DIR, exist_ok=True)

moved = []
for pattern in PATTERNS:
    for p in ROOT.glob(pattern):
        dest = LARGE_DIR / p.name
        print(f"Moving {p} -> {dest}")
        shutil.move(str(p), str(dest))
        moved.append(dest)

if ROOT_MODELS_DIR.exists():
    for item in ROOT_MODELS_DIR.iterdir():
        dest = LARGE_DIR / item.name
        if item.is_dir():
            if dest.exists():
                for subitem in item.iterdir():
                    subdest = dest / subitem.name
                    print(f"Moving {subitem} -> {subdest}")
                    shutil.move(str(subitem), str(subdest))
                    moved.append(subdest)
                item.rmdir()
            else:
                print(f"Moving directory {item} -> {dest}")
                shutil.move(str(item), str(dest))
        else:
            if dest.exists():
                print(f"Skipping existing {dest}")
                continue
            print(f"Moving {item} -> {dest}")
            shutil.move(str(item), str(dest))
            moved.append(dest)
    try:
        ROOT_MODELS_DIR.rmdir()
    except OSError:
        pass

# Add gitignore entry
gitignore = ROOT / ".gitignore"
entry = "# Large prebuilt models for offline storage\n/backend/large_models/*\n/models/\nmodels*_*\\.pkl\n"
if gitignore.exists():
    text = gitignore.read_text()
    if "/backend/large_models/" not in text or "/models/" not in text:
        gitignore.write_text(text + "\n" + entry)
else:
    gitignore.write_text(entry)

print(f"Moved {len(moved)} files to {LARGE_DIR}")
for m in moved:
    print(str(m))
print("Done. Commit the changes (models moved and .gitignore updated).\nOn Streamlit Cloud, set the environment variable STREAMLIT_CLOUD=1 to enable safe fallback mode.")
