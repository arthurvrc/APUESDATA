import pandas as pd
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
PROCESSED = ROOT / "data" / "processed"

def compute_xg_proxies(df):
    """
    xG proxy inspiré des métriques FBref :
    - Poids élevé sur tirs cadrés
    - Poids modéré sur tirs totaux
    - Bonus pour positions dangereuses (dérivé buts)
    """
    df = df.copy()

    # ⚽ Tirs totaux approximés
    df["shots_for"] = df["HomeGoals"] * 6 + 4
    df["shots_against"] = df["AwayGoals"] * 6 + 4

    # 🎯 Tirs cadrés proxy
    df["sot_for"] = df["HomeGoals"] * 3 + 2
    df["sot_against"] = df["AwayGoals"] * 3 + 2

    # 🔥 xG proxy
    df["xg_for"] = (
        df["shots_for"] * 0.08 +
        df["sot_for"] * 0.23 +
        df["HomeGoals"] * 0.45
    )

    df["xg_against"] = (
        df["shots_against"] * 0.08 +
        df["sot_against"] * 0.23 +
        df["AwayGoals"] * 0.45
    )

    return df


def compute_xg_rolling(df):
    """
    Rolling xG / xGA sur 5 et 10 matches
    """
    df = df.sort_values("Date").copy()

    df["xg_roll_5"] = df["xg_for"].rolling(5, min_periods=1).mean()
    df["xga_roll_5"] = df["xg_against"].rolling(5, min_periods=1).mean()

    df["xg_roll_10"] = df["xg_for"].rolling(10, min_periods=1).mean()
    df["xga_roll_10"] = df["xg_against"].rolling(10, min_periods=1).mean()

    df["xg_diff_roll_5"] = df["xg_roll_5"] - df["xga_roll_5"]
    df["xg_diff_roll_10"] = df["xg_roll_10"] - df["xga_roll_10"]

    return df


def add_xg_features(df):
    """
    Fonction appelée depuis rebuild_features.py
    Ajoute :
    - xG_for / xG_against
    - rolling xG (5 / 10)
    - xG_diff
    """
    df = df.copy()

    df = compute_xg_proxies(df)
    df = compute_xg_rolling(df)

    # xG gap brut
    df["xg_diff"] = df["xg_for"] - df["xg_against"]

    return df
