# =========================================
# TRAIN XGB PRO – APUESDATA (NO OPTUNA)
# =========================================

import json
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.calibration import CalibratedClassifierCV
from xgboost import XGBClassifier
import joblib

from src.config import MODELS

# -----------------------------------------
# Load feature columns
# -----------------------------------------
feature_cols_path = MODELS / "feature_cols.json"
with open(feature_cols_path, "r") as f:
    FEATURE_COLS = json.load(f)

# -----------------------------------------
# Paths
# -----------------------------------------
DATASET = Path("data/processed/all_matches_features.csv")
MODEL_FILE = MODELS / "xgb_model.pkl"
CALIBRATOR_FILE = MODELS / "calibrators.pkl"
MEDIANS_FILE = MODELS / "medians.json"


# =========================================
# TRAINING FUNCTION
# =========================================
def train_model():
    print("🔧 Loading dataset...")

    df = pd.read_csv(DATASET)

    # --------- CLEANING ----------
    df = df[df["target_1x2"].isin([0, 1, 2])]

    df = df[FEATURE_COLS + ["target_1x2"]].copy()

    df = df.replace([np.inf, -np.inf], np.nan)
    medians = df.median()
    df = df.fillna(medians)

    medians.to_json(MEDIANS_FILE)
    print(f"💾 Saved medians → {MEDIANS_FILE}")

    # -----------------------------------
    # SPLIT DATA
    # -----------------------------------
    X = df[FEATURE_COLS]
    y = df["target_1x2"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.15, random_state=42, stratify=y
    )

    # -----------------------------------
    # TRAIN XGBOOST (stable config)
    # -----------------------------------
    print("🚀 Training XGBoost PRO model...")

    model = XGBClassifier(
        n_estimators=450,
        learning_rate=0.04,
        max_depth=7,
        subsample=0.85,
        colsample_bytree=0.85,
        eval_metric="mlogloss",
        random_state=42,
        tree_method="hist"
    )

    model.fit(X_train, y_train)

    # -----------------------------------
    # CALIBRATION
    # -----------------------------------
    print("📏 Calibrating probabilities...")
    calibrator = CalibratedClassifierCV(model, method="isotonic", cv=3)
    calibrator.fit(X_train, y_train)

    # -----------------------------------
    # SAVE ARTIFACTS
    # -----------------------------------
    joblib.dump(model, MODEL_FILE)
    joblib.dump(calibrator, CALIBRATOR_FILE)

    print(f"💾 Saved model → {MODEL_FILE}")
    print(f"💾 Saved calibrator → {CALIBRATOR_FILE}")
    print("✔ Training complete!")


if __name__ == "__main__":
    train_model()
