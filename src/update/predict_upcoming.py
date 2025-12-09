# ==========================================
# PREDICT UPCOMING FIXTURES – APUESDATA PRO
# ==========================================

import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from src.config import PROCESSED, MODELS
from src.model_loader import load_model_bundle

INPUT_FILE = PROCESSED / "predictions_upcoming_features.csv"
OUTPUT_FILE = PROCESSED / "predictions_upcoming.csv"


def predict():
    print(f"📥 Loading upcoming features from {INPUT_FILE}")
    df = pd.read_csv(INPUT_FILE)

    # --------------------------------------------
    # Load model + calibrator + medians + features
    # --------------------------------------------
    print("🔧 Loading model bundle...")
    model, feature_names, medians, calibrator = load_model_bundle()
    print("✔ Model bundle loaded successfully.")

    # --------------------------------------------
    # FIX: KEEP fixture_id, HomeTeam, AwayTeam
    # --------------------------------------------
    meta_cols = ["fixture_id", "HomeTeam", "AwayTeam", "Date"]
    available_meta = [c for c in meta_cols if c in df.columns]
    meta = df[available_meta].copy()

    # --------------------------------------------
    # Prepare X
    # --------------------------------------------
    X = df[feature_names].copy()
    X = X.replace([np.inf, -np.inf], np.nan)
    X = X.fillna(medians)

    # --------------------------------------------
    # Predict raw & calibrated probabilities
    # --------------------------------------------
    p_raw = model.predict_proba(X)
    p_cal = calibrator.predict_proba(X)

    df_out = meta.copy()
    df_out["p_raw_home"] = p_raw[:, 0]
    df_out["p_raw_draw"] = p_raw[:, 1]
    df_out["p_raw_away"] = p_raw[:, 2]

    df_out["p_home"] = p_cal[:, 0]
    df_out["p_draw"] = p_cal[:, 1]
    df_out["p_away"] = p_cal[:, 2]

    # --------------------------------------------
    # Save final predictions
    # --------------------------------------------
    df_out.to_csv(OUTPUT_FILE, index=False)
    print(f"📦 Saved calibrated predictions → {OUTPUT_FILE} (shape= {df_out.shape} )")
    print("✔️ Predict upcoming fixtures OK")


if __name__ == "__main__":
    predict()
