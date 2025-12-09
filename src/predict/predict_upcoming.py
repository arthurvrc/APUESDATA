import pandas as pd
import json
import pickle
from pathlib import Path
import numpy as np
from src.model_loader import load_model_bundle

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "processed"

FEATURES = DATA / "predictions_upcoming_features.csv"
OUT = DATA / "predictions_upcoming.csv"


def predict():
    print("📥 Loading upcoming features from", FEATURES)
    df = pd.read_csv(FEATURES)

    # -------------------------
    # 1) Load model + metadata
    # -------------------------
    print("🔧 Model bundle loaded successfully.")
    model, feature_names, medians, calibrator = load_model_bundle()

    # Keep only features expected by model
    X = df[feature_names].copy()

    # Replace missing values
    X = X.fillna(medians)

    # -------------------------
    # 2) Raw model probabilities
    # -------------------------
    p_raw = model.predict_proba(X)

    df["p_raw_home"] = p_raw[:, 0]
    df["p_raw_draw"] = p_raw[:, 1]
    df["p_raw_away"] = p_raw[:, 2]

    # -------------------------
    # 3) Soft clipping 
    # -------------------------
    def softclip(v):
        v = np.clip(v, 0.05, 0.85)
        return v

    df["p_home"] = softclip(df["p_raw_home"])
    df["p_draw"] = softclip(df["p_raw_draw"])
    df["p_away"] = softclip(df["p_raw_away"])

    # Re-normalisation 
    s = df[["p_home", "p_draw", "p_away"]].sum(axis=1)
    df["p_home"] /= s
    df["p_draw"] /= s
    df["p_away"] /= s

    # -------------------------
    # 4) Save final CSV
    # -------------------------
    df.to_csv(OUT, index=False)
    print("📦 Saved calibrated predictions →", OUT, "(shape=", df.shape, ")")
    print("✔️ Predict upcoming fixtures OK")


if __name__ == "__main__":
    predict()
