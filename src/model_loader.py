# =========================================
# MODEL LOADER – APUESDATA
# =========================================
import json
import joblib
from pathlib import Path

from src.config import MODEL_FILE, CALIBRATOR_FILE, FEATURE_COLS, MEDIANS_FILE

def load_model_bundle():
    print("🔧 Loading model bundle...")

    # -------- LOAD MODEL --------
    model = joblib.load(MODEL_FILE)

    # -------- LOAD CALIBRATOR (joblib, NOT pickle) --------
    calibrator = joblib.load(CALIBRATOR_FILE)

    # -------- LOAD FEATURES --------
    with open(FEATURE_COLS, "r") as f:
        feature_names = json.load(f)

    # -------- LOAD MEDIANS --------
    with open(MEDIANS_FILE, "r") as f:
        medians = json.load(f)

    print("✔ Model bundle loaded successfully.")
    return model, feature_names, medians, calibrator
