import os
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROCESSED = ROOT / "data" / "processed"

HIST = PROCESSED / "all_matches_features.csv"
UPCOMING = ROOT / "data" / "upcoming_api.csv"
OUT = PROCESSED / "predictions_upcoming_features.csv"


def build_upcoming_features():
    print("🔧 Loading datasets...")

    if not HIST.exists():
        raise FileNotFoundError(f"❌ Missing historical features: {HIST}")

    if not UPCOMING.exists():
        raise FileNotFoundError(f"❌ Missing upcoming API file: {UPCOMING}")

    df_hist = pd.read_csv(HIST, parse_dates=["Date"], low_memory=False)
    df_upc = pd.read_csv(UPCOMING)

    print(f"📥 History: {df_hist.shape}")
    print(f"📥 Upcoming: {df_upc.shape}")

    # Normalisation des noms
    df_hist["HomeTeam"] = df_hist["HomeTeam"].str.lower()
    df_hist["AwayTeam"] = df_hist["AwayTeam"].str.lower()

    # Conserver uniquement les features utiles
    df_hist = df_hist.sort_values("Date")

    # Récupérer dernière ligne par équipe (home / away)
    latest_home = df_hist.groupby("HomeTeam").tail(1).add_prefix("home_")
    latest_away = df_hist.groupby("AwayTeam").tail(1).add_prefix("away_")

    # Merge avec upcoming
    df = df_upc.merge(
        latest_home,
        left_on="home_name",
        right_on="home_HomeTeam",
        how="left"
    ).merge(
        latest_away,
        left_on="away_name",
        right_on="away_AwayTeam",
        how="left"
    )

    # Supprimer les colonnes inutiles
    df = df.drop(columns=[
        "home_HomeTeam", "away_AwayTeam"
    ], errors="ignore")

    # Sauvegarde
    os.makedirs(PROCESSED, exist_ok=True)
    df.to_csv(OUT, index=False)

    print(f"💾 Saved: {OUT} (shape={df.shape})")
    print("✔ Upcoming features ready for prediction.")


if __name__ == "__main__":
    build_upcoming_features()
