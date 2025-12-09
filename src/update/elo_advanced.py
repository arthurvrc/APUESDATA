import pandas as pd
import numpy as np

# --------------------------------------------------
# Advanced Elo System for APUESDATA
# --------------------------------------------------

K = 25
HOME_ADV = 80  # home advantage boost

def expected_score(r1, r2):
    return 1 / (1 + 10 ** ((r2 - r1) / 400))

def update_elo(r_home, r_away, goals_home, goals_away):
    exp_home = expected_score(r_home + HOME_ADV, r_away)

    if goals_home > goals_away:
        s_home = 1
    elif goals_home == goals_away:
        s_home = 0.5
    else:
        s_home = 0

    new_home = r_home + K * (s_home - exp_home)
    new_away = r_away + K * ((1 - s_home) - (1 - exp_home))

    return new_home, new_away

def compute_elo(df):
    teams = pd.unique(df[["HomeTeam", "AwayTeam"]].values.ravel())
    ratings = {t: 1500 for t in teams}

    elo_home_list = []
    elo_away_list = []

    for _, row in df.iterrows():
        h, a = row["HomeTeam"], row["AwayTeam"]
        hg, ag = row["HomeGoals"], row["AwayGoals"]

        r_home = ratings[h]
        r_away = ratings[a]

        elo_home_list.append(r_home)
        elo_away_list.append(r_away)

        new_r_home, new_r_away = update_elo(r_home, r_away, hg, ag)
        ratings[h], ratings[a] = new_r_home, new_r_away

    df["elo_home"] = elo_home_list
    df["elo_away"] = elo_away_list
    return df
