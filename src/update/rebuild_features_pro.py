# =========================================
# REBUILD FEATURES PRO – APUESDATA
# =========================================
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # projet / APUESDATA
sys.path.insert(0, str(ROOT))

from utils.standardize_features import standardize_history
import pandas as pd
import numpy as np

from src.config import HISTORY, HIST_FEATURES


def rebuild_all_features():
    print("🔧 Loading RAW datasets...")

    # 🔥 Correction principale : fichier correct
    hist_file = HISTORY / "history.csv"

    if not hist_file.exists():
        print(f"❌ History file not found → {hist_file}")
        return

    try:
        df = pd.read_csv(hist_file)
    except Exception as e:
        print("❌ Failed to load history:", e)
        return

    if df.empty:
        print("⚠️ Empty history file.")
        return

    # Clean + normalize
    df = standardize_history(df)
    df = df.sort_values("Date").reset_index(drop=True)

    # ------------------------------------------
    # Compute statistical features PRO
    # ------------------------------------------
    def compute_team_features(team, n):
        matches = df[(df["HomeTeam"] == team) | (df["AwayTeam"] == team)].tail(n)

        if matches.empty:
            return 0, 0, 0

        gf, ga, pts = [], [], []

        for _, m in matches.iterrows():
            is_home = m["HomeTeam"] == team

            gf_match = m["HomeGoals"] if is_home else m["AwayGoals"]
            ga_match = m["AwayGoals"] if is_home else m["HomeGoals"]

            gf.append(gf_match)
            ga.append(ga_match)

            if gf_match > ga_match:
                pts.append(3)
            elif gf_match == ga_match:
                pts.append(1)
            else:
                pts.append(0)

        return np.mean(gf), np.mean(ga), np.mean(pts)

    # Build rows
    feature_rows = []

    for _, row in df.iterrows():
        home = row["HomeTeam"]
        away = row["AwayTeam"]

        # Last 5
        home_gf5, home_ga5, home_pts5 = compute_team_features(home, 5)
        away_gf5, away_ga5, away_pts5 = compute_team_features(away, 5)

        # Last 10
        home_gf10, home_ga10, home_pts10 = compute_team_features(home, 10)
        away_gf10, away_ga10, away_pts10 = compute_team_features(away, 10)

        feature_rows.append({
            "fixture_id": row.get("fixture_id"),
            "Date": row["Date"],
            "HomeTeam": home,
            "AwayTeam": away,
            "HomeGoals": row.get("HomeGoals"),
            "AwayGoals": row.get("AwayGoals"),

            # Last 5
            "home_gf5": home_gf5,
            "home_ga5": home_ga5,
            "home_pts5": home_pts5,
            "away_gf5": away_gf5,
            "away_ga5": away_ga5,
            "away_pts5": away_pts5,

            # Last 10
            "home_gf10": home_gf10,
            "home_ga10": home_ga10,
            "home_pts10": home_pts10,
            "away_gf10": away_gf10,
            "away_ga10": away_ga10,
            "away_pts10": away_pts10,
        })

    df_features = pd.DataFrame(feature_rows)
    df_features.to_csv(HIST_FEATURES, index=False)

    print(f"💾 Saved historical features → {HIST_FEATURES}  (shape={df_features.shape})")
    return df_features


if __name__ == "__main__":
    rebuild_all_features()
