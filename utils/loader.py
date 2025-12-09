# =========================================
# LOADER UTILS – APUESDATA
# =========================================

import pandas as pd
from pathlib import Path


def load_csv(path: Path, parse_date_cols=None):
    """
    Charge un CSV de manière robuste :
    - retourne un DataFrame vide si le fichier n'existe pas
    - convertit automatiquement les dates
    """

    if not path.exists():
        print(f"⚠️  Fichier introuvable : {path}")
        return pd.DataFrame()

    try:
        df = pd.read_csv(path)
    except Exception as e:
        print(f"❌ Erreur de lecture CSV ({path}): {e}")
        return pd.DataFrame()

    # Colonnes de dates
    if parse_date_cols:
        for col in parse_date_cols:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce")

    return df


def auto_detect_date(df):
    """Détecte automatiquement une colonne date dans un DataFrame"""
    candidates = ["date", "Date", "fixture_date", "utc_date", "timestamp"]
    for c in candidates:
        if c in df.columns:
            return c
    return None


def load_upcoming_csv(path: Path):
    """
    Charge upcoming_api.csv en détectant automatiquement :
    - la colonne date
    - les colonnes équipes
    """

    if not path.exists():
        print("⚠️ Aucun upcoming_api.csv trouvé.")
        return pd.DataFrame()

    df = pd.read_csv(path)

    # DATE
    date_col = auto_detect_date(df)
    if date_col is None:
        print("❌ Impossible de détecter une colonne date dans upcoming_api.csv")
        return pd.DataFrame()

    df["Date"] = pd.to_datetime(df[date_col], errors="coerce", utc=True)
    df["Date"] = df["Date"].dt.tz_convert(None)

    # EQUIPES
    HOME = ["home_name", "HomeTeam", "homeTeam", "team_home"]
    AWAY = ["away_name", "AwayTeam", "awayTeam", "team_away"]

    home_col = next((c for c in HOME if c in df.columns), None)
    away_col = next((c for c in AWAY if c in df.columns), None)

    if not home_col or not away_col:
        print("❌ Impossible de détecter Home/Away dans upcoming_api.csv")
        return pd.DataFrame()

    df["HomeTeam"] = df[home_col].astype(str).str.lower()
    df["AwayTeam"] = df[away_col].astype(str).str.lower()

    df["match"] = df["HomeTeam"] + " vs " + df["AwayTeam"]

    return df.sort_values("Date").reset_index(drop=True)
