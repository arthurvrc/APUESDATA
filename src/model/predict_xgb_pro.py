# src/model/predict_xgb_pro.py

import pandas as pd
import numpy as np
import pickle
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
PROCESSED = DATA / "processed"

UPCOMING_FEATURES = PROCESSED / "predictions_upcoming_features.csv"
MODEL_BUNDLE = ROOT / "model_bundle.pkl"
OUTPUT = PROCESSED / "predictions_upcoming.csv"


def load_bundle():
    with open(MODEL_BUNDLE, "rb") as f:
        bundle = pickle.load(f)
    return bundle["scaler"], bundle["model"], bundle["calibrator"], bundle["features"]


def predict_upcoming():
    print("📥 Loading upcoming PRO features…")
    df = pd.read_csv(UPCOMING_FEATURES)

    scaler, model, calibrator, feat_cols = load_bundle()

    # Vérification des colonnes
    for c in feat_cols:
        if c not in df.columns:
            print(f"⚠️ Feature manquante dans upcoming: {c}")
            df[c] = 0  # fallback

    X = df[feat_cols].fillna(0)

    X_scaled = scaler.transform(X)

    print("🔮 Predicting (raw XGB)…")
    raw_preds = model.predict_proba(X_scaled)

    print("🧪 Calibrating predictions…")
    preds = calibrator.predict_proba(X_scaled)

    output = df.copy()
    output["p_home"] = preds[:, 2] * 100
    output["p_draw"] = preds[:, 1] * 100
    output["p_away"] = preds[:, 0] * 100

    output.to_csv(OUTPUT, index=False)
    print(f"💾 Saved calibrated predictions → {OUTPUT}")

    return output


if __name__ == "__main__":
    predict_upcoming()
