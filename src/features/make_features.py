import pandas as pd
from pathlib import Path

HIST = Path("data/all_matches_raw.csv")
UPCOMING = Path("data/upcoming_api.csv")
OUTPUT = Path("data/upcoming_features.csv")

def compute_features():
    hist = pd.read_csv(HIST)
    up = pd.read_csv(UPCOMING)

    # ELO simple
    hist["elo_diff"] = (hist["home_goals"] - hist["away_goals"]).fillna(0)

    elo = hist.groupby("home_name")["elo_diff"].mean()

    up["elo_home"] = up["home_name"].map(elo).fillna(0)
    up["elo_away"] = up["away_name"].map(elo).fillna(0)

    # Forme simple
    hist["result"] = (hist["home_goals"] > hist["away_goals"]).astype(int)
    form = hist.groupby("home_name")["result"].rolling(5).mean().reset_index(0, drop=True)
    hist["form"] = form

    up["form_home"] = up["home_name"].map(hist.groupby("home_name")["form"].last()).fillna(0.5)
    up["form_away"] = up["away_name"].map(hist.groupby("away_name")["form"].last()).fillna(0.5)

    up.to_csv(OUTPUT, index=False)
    print(f"✔ Features generated → {OUTPUT}")

if __name__ == "__main__":
    compute_features()
