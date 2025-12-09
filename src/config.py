# =========================================
# CONFIGURATION APUESDATA (PRO)
# =========================================

import os
from pathlib import Path
from dotenv import load_dotenv

# 🔧 Charger automatiquement .env
load_dotenv()

# -----------------------------------------
# 🔑 Variables API (depuis .env)
# -----------------------------------------
API_FOOTBALL_KEY = os.getenv("API_FOOTBALL_KEY")
API_FOOTBALL_HOST = os.getenv("API_FOOTBALL_HOST")

if not API_FOOTBALL_KEY:
    raise ValueError("❌ ERREUR : API_FOOTBALL_KEY manquante dans .env")

if not API_FOOTBALL_HOST:
    raise ValueError("❌ ERREUR : API_FOOTBALL_HOST manquante dans .env")

# -----------------------------------------
# 📁 STRUCTURE DES DOSSIERS
# -----------------------------------------
ROOT = Path(__file__).resolve().parents[1]

DATA = ROOT / "data"
RAW = DATA / "raw"
PROCESSED = DATA / "processed"
HISTORY = RAW / "history"
MODELS = ROOT / "models"

# Créer auto les dossiers s'ils n'existent pas
for d in [DATA, RAW, PROCESSED, HISTORY, MODELS]:
    d.mkdir(parents=True, exist_ok=True)

# -----------------------------------------
# 📄 FICHIERS RAW
# -----------------------------------------
RAW_FIX = RAW / "fixtures_api.csv"
RAW_RES = RAW / "results_api.csv"
RAW_LAST_RES = RAW / "last_results_api.csv"
UPCOMING = RAW / "upcoming_api.csv"

# -----------------------------------------
# 📄 FICHIERS PROCESSED
# -----------------------------------------
HIST_FEATURES = PROCESSED / "all_matches_features_updated.csv"
UPCOMING_FEATURES = PROCESSED / "predictions_upcoming_features.csv"
UPCOMING_PRED = PROCESSED / "predictions_upcoming.csv"
VALUE_BETS = PROCESSED / "bets_recommendations.csv"

# -----------------------------------------
# 🧠 MODELS
# -----------------------------------------
MODEL_FILE = MODELS / "xgb_model.pkl"
CALIBRATOR_FILE = MODELS / "calibrators.pkl"
FEATURE_COLS = MODELS / "feature_cols.json"
MEDIANS_FILE = MODELS / "medians.json"
