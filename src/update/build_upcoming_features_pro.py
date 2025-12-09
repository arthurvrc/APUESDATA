# ==========================================================
# BUILD UPCOMING FEATURES PRO — FULLY FIXED VERSION
# ==========================================================

import pandas as pd
import numpy as np
from pathlib import Path
from tqdm import tqdm
import json
from src.config import DATA, MODELS

# Load feature list expected by model
FEATURE_COLS = json.load(open(MODELS / "feature_cols.json"))

# Load historical dataset (full features)
HISTORY = pd.read_csv(DATA / "processed" / "all_matches_features.csv", low_memory=False)
HISTORY["Date"] = pd.to_datetime(HISTORY["Date"], errors="coerce")

# Fast indexes
INDEXED = {
    "teams": list(set(HISTORY["HomeTeam"]) | set(HISTORY["AwayTeam"]))
}


# ----------------------------------------------------------
# Helper: last N match stats
# ----------------------------------------------------------
def last_n_matches(team, n):
    df = HISTORY[(HISTORY["HomeTeam"] == team) | (HISTORY["AwayTeam"] == team)]
    df = df.sort_values("Date").tail(n)

    if df.empty:
        return {
            "gf": 0, "ga": 0, "pts": 0, "btts": 0, "over25": 0
        }

    gf, ga, pts, btts, over25 = [], [], [], [], []

    for _, m in df.iterrows():
        if m["HomeTeam"] == team:
            g_for, g_against = m["HomeGoals"], m["AwayGoals"]
        else:
            g_for, g_against = m["AwayGoals"], m["HomeGoals"]

        gf.append(g_for)
        ga.append(g_against)

        pts.append(3 if g_for > g_against else 1 if g_for == g_against else 0)
        btts.append(1 if g_for > 0 and g_against > 0 else 0)
        over25.append(1 if (g_for + g_against) >= 3 else 0)

    return {
        "gf": np.mean(gf),
        "ga": np.mean(ga),
        "pts": np.mean(pts),
        "btts": np.mean(btts),
        "over25": np.mean(over25),
    }


# ----------------------------------------------------------
# Season-level stats
# ----------------------------------------------------------
def season_stats(team):
    df = HISTORY[(HISTORY["HomeTeam"] == team) | (HISTORY["AwayTeam"] == team)]

    if df.empty:
        return {
            "winrate": 0, "drawrate": 0, "lossrate": 0,
            "gf_avg": 0, "ga_avg": 0
        }

    wins, draws, losses, gf, ga = 0, 0, 0, 0, 0

    for _, m in df.iterrows():
        if m["HomeTeam"] == team:
            g_for, g_against = m["HomeGoals"], m["AwayGoals"]
        else:
            g_for, g_against = m["AwayGoals"], m["HomeGoals"]

        gf += g_for
        ga += g_against

        if g_for > g_against:
            wins += 1
        elif g_for == g_against:
            draws += 1
        else:
            losses += 1

    total = len(df)
    return {
        "winrate": wins / total,
        "drawrate": draws / total,
        "lossrate": losses / total,
        "gf_avg": gf / total,
        "ga_avg": ga / total
    }


# ----------------------------------------------------------
# MAIN BUILD FUNCTION
# ----------------------------------------------------------
def build():
    print(f"📌 Model expects {len(FEATURE_COLS)} features.")

    # Load API fixtures
    upcoming = pd.read_csv(DATA / "raw" / "upcoming_api.csv")

    upcoming.rename(columns={
        "home_name": "HomeTeam",
        "away_name": "AwayTeam",
        "date": "Date",
    }, inplace=True)

    upcoming["Date"] = pd.to_datetime(upcoming["Date"], errors="coerce")
    up = upcoming.dropna(subset=["HomeTeam", "AwayTeam"])

    print(f"📚 Loaded {len(up)} upcoming fixtures.")

    rows = []

    for _, r in tqdm(up.iterrows(), total=len(up)):
        home, away = r["HomeTeam"], r["AwayTeam"]

        # Retrieve stats
        h5 = last_n_matches(home, 5)
        a5 = last_n_matches(away, 5)
        h10 = last_n_matches(home, 10)
        a10 = last_n_matches(away, 10)

        sh = season_stats(home)
        sa = season_stats(away)

        row = {
            "elo_home": 1500,  # placeholder if missing
            "elo_away": 1500,
            "home_gf_avg_last_5": h5["gf"],
            "home_ga_avg_last_5": h5["ga"],
            "home_points_avg_last_5": h5["pts"],
            "home_btts_rate_last_5": h5["btts"],
            "home_over25_rate_last_5": h5["over25"],
            "home_gf_avg_last_10": h10["gf"],
            "home_ga_avg_last_10": h10["ga"],
            "home_points_avg_last_10": h10["pts"],
            "home_btts_rate_last_10": h10["btts"],
            "home_over25_rate_last_10": h10["over25"],

            "away_gf_avg_last_5": a5["gf"],
            "away_ga_avg_last_5": a5["ga"],
            "away_points_avg_last_5": a5["pts"],
            "away_btts_rate_last_5": a5["btts"],
            "away_over25_rate_last_5": a5["over25"],
            "away_gf_avg_last_10": a10["gf"],
            "away_ga_avg_last_10": a10["ga"],
            "away_points_avg_last_10": a10["pts"],
            "away_btts_rate_last_10": a10["btts"],
            "away_over25_rate_last_10": a10["over25"],

            "home_winrate_season": sh["winrate"],
            "home_drawrate_season": sh["drawrate"],
            "home_lossrate_season": sh["lossrate"],
            "home_goals_for_avg_season": sh["gf_avg"],
            "home_goals_against_avg_season": sh["ga_avg"],

            "away_winrate_season": sa["winrate"],
            "away_drawrate_season": sa["drawrate"],
            "away_lossrate_season": sa["lossrate"],
            "away_goals_for_avg_season": sa["gf_avg"],
            "away_goals_against_avg_season": sa["ga_avg"],

            # BOOKMAKER placeholders (0 to avoid crash)
            "BWH": 0, "BWD": 0, "BWA": 0,
            "IWH": 0, "IWD": 0, "IWA": 0,
            "WHH": 0, "WHD": 0, "WHA": 0,
            "VCH": 0, "VCD": 0, "VCA": 0,
        }

        # Add missing columns that model expects but not produced
        for col in FEATURE_COLS:
            if col not in row:
                row[col] = row.get(col, 0)

        rows.append(row)

    df = pd.DataFrame(rows)

    df.to_csv(DATA / "processed" / "predictions_upcoming_features.csv", index=False)

    print(f"💾 Saved → {DATA / 'processed/predictions_upcoming_features.csv'} (shape={df.shape})")
    print("✔ build_upcoming_features_pro OK.")


if __name__ == "__main__":
    build()
