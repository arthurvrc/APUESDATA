# ==========================================
# COMPUTE VALUE BETS – APUESDATA PRO
# ==========================================

import pandas as pd
import numpy as np
from pathlib import Path
from src.config import PROCESSED

PRED_FILE = PROCESSED / "predictions_upcoming.csv"
OUTPUT_FILE = PROCESSED / "bets_recommendations.csv"

def compute_value_bets():
    print(f"📥 Loading predictions from {PRED_FILE}")

    df = pd.read_csv(PRED_FILE)

    # Ensure required columns exist
    required = ["fixture_id", "HomeTeam", "AwayTeam",
                "p_home", "p_draw", "p_away"]
    for col in required:
        if col not in df.columns:
            print(f"❌ ERROR: Missing column: {col}")
            return

    # If odds do not exist, create neutral odds
    if "odds_home_mean" not in df.columns:
        df["odds_home_mean"] = 1 / df["p_home"].clip(0.01)
        df["odds_draw_mean"] = 1 / df["p_draw"].clip(0.01)
        df["odds_away_mean"] = 1 / df["p_away"].clip(0.01)

    rows = []

    for _, r in df.iterrows():

        ev_home = r.p_home * r.odds_home_mean - 1
        ev_draw = r.p_draw * r.odds_draw_mean - 1
        ev_away = r.p_away * r.odds_away_mean - 1

        best_ev = max(ev_home, ev_draw, ev_away)
        best_bet = ["HOME", "DRAW", "AWAY"][np.argmax([ev_home, ev_draw, ev_away])]

        rows.append({
            "fixture_id": r.fixture_id,
            "HomeTeam": r.HomeTeam,
            "AwayTeam": r.AwayTeam,
            "p_home": r.p_home,
            "p_draw": r.p_draw,
            "p_away": r.p_away,
            "odds_home_mean": r.odds_home_mean,
            "odds_draw_mean": r.odds_draw_mean,
            "odds_away_mean": r.odds_away_mean,
            "EV_home": ev_home,
            "EV_draw": ev_draw,
            "EV_away": ev_away,
            "BestBet": best_bet,
            "BestEV": best_ev,
        })

    out = pd.DataFrame(rows)
    out.to_csv(OUTPUT_FILE, index=False)
    print(f"💾 Saved value bets → {OUTPUT_FILE}")


if __name__ == "__main__":
    compute_value_bets()
