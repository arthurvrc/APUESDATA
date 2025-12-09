# ============================================
#   EVALUATE XGB PRO MODEL ON HISTORICAL DATA
# ============================================

import json
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    classification_report,
    log_loss
)
import joblib
from src.config import MODELS

# --------------------------
# Load artifacts
# --------------------------
MODEL_FILE = MODELS / "xgb_model.pkl"
CALIB_FILE = MODELS / "calibrators.pkl"
FEATURE_COLS_FILE = MODELS / "feature_cols.json"
MEDIANS_FILE = MODELS / "medians.json"
DATASET = Path("data/processed/all_matches_features.csv")

model = joblib.load(MODEL_FILE)

try:
    calibrator = joblib.load(CALIB_FILE)
    USE_CALIBRATOR = True
except:
    calibrator = model
    USE_CALIBRATOR = False

with open(FEATURE_COLS_FILE, "r") as f:
    FEATURE_COLS = json.load(f)

with open(MEDIANS_FILE, "r") as f:
    MEDIANS = json.load(f)


# --------------------------
# Load dataset
# --------------------------
print("📥 Loading dataset…")
df = pd.read_csv(DATASET, low_memory=False)

df = df[df["target_1x2"].isin([0, 1, 2])]

X = df[FEATURE_COLS].copy()
y = df["target_1x2"].copy()

# Fill missing with medians
X = X.fillna(MEDIANS)


# --------------------------
# Prediction
# --------------------------
print("🔮 Predicting…")

probs = calibrator.predict_proba(X)
preds = np.argmax(probs, axis=1)

# --------------------------
# Metrics
# --------------------------
acc = accuracy_score(y, preds)
cm = confusion_matrix(y, preds)
ll = log_loss(y, probs)

print("\n==============================")
print("📊 MODEL PERFORMANCE (XGB PRO)")
print("==============================\n")

print(f"✔ Accuracy: {acc*100:.2f}%")
print(f"✔ Log Loss: {ll:.4f}")
print("\nConfusion Matrix:")
print(cm)

print("\nClassification Report:")
print(classification_report(y, preds, digits=3))

print("\nCalibration:")
print(f"Calibrator used: {USE_CALIBRATOR}")

print("\nDone ✓")

