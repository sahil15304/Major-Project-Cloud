import pandas as pd
from pathlib import Path
from typing import List
import json

from app.models import ModelManager

BASE_DIR = Path(__file__).resolve().parents[1]


def _ensure_features(df: pd.DataFrame, required: List[str]):
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def process_and_predict_file(csv_path: str) -> str:
    """Process input CSV and run predictions for available models.

    Returns path to output CSV with predictions appended.
    """
    df = pd.read_csv(csv_path)

    # Very small preprocessing: drop rows with NaNs in required fields
    expected_order = ["AGE", "SEX", "NP1TOT", "NP2TOT", "NP3TOT", "MCATOT", "SEVERITY"]
    _ensure_features(df, expected_order)

    mgr = ModelManager()
    mgr.load_all_models()

    # For each loaded model, produce a prediction column
    for model_name in mgr.list_models():
        preds = []
        for _, row in df.iterrows():
            features = [float(row[f]) for f in expected_order]
            p = mgr.predict(model_name, features)
            preds.append(p)
        col = f"pred_{model_name}"
        df[col] = preds

    out_dir = BASE_DIR / "processed_uploads"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / (Path(csv_path).stem + "_predictions.csv")
    df.to_csv(out_path, index=False)

    # Optionally save a small metadata file
    meta = {
        "source": str(csv_path),
        "rows": len(df),
        "models": mgr.list_models(),
    }
    with (out_dir / (Path(csv_path).stem + "_meta.json")).open("w") as f:
        json.dump(meta, f)

    return str(out_path)


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: process_and_predict.py <csv_path>")
        raise SystemExit(2)
    print(process_and_predict_file(sys.argv[1]))
