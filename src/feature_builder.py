import pandas as pd
import numpy as np
from pathlib import Path

# ============================================================
# PATHS & RAW DATA
# ============================================================

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"

# Lineups (optionnel – pour plus tard)
LINEUPS_PATH = RAW / "lineups_api.csv"
df_lineups = pd.read_csv(LINEUPS_PATH) if LINEUPS_PATH.exists() else None


# ============================================================
# HELPERS
# ============================================================

def normalize_team(x):
    return x.lower().strip() if isinstance(x, str) else x


def compute_market_probabilities(odds_H, odds_D, odds_A):
    """
    Transforme des cotes (décimales) en probabilités implicites corrigées du overround.
    """
    if odds_H is None or odds_D is None or odds_A is None:
        return 0.33, 0.33, 0.33

    try:
        pH = 1.0 / float(odds_H)
        pD = 1.0 / float(odds_D)
        pA = 1.0 / float(odds_A)
    except Exception:
        return 0.33, 0.33, 0.33

    s = pH + pD + pA
    if s <= 0:
        return 0.33, 0.33, 0.33

    return pH / s, pD / s, pA / s


# ============================================================
# FORM FEATURES (5 & 10 LAST MATCHES)
# ============================================================

def get_last_matches(df, team, date, n=10):
    tmp = df[
        ((df["HomeTeam"] == team) | (df["AwayTeam"] == team))
        & (df["Date"] < date)
    ].sort_values("Date", ascending=False).head(n)
    return tmp


def compute_form(df, team, date):
    last10 = get_last_matches(df, team, date, 10).copy()
    last5 = last10.head(5).copy()

    if last10.empty:
        return dict(
            gf5=0.0, ga5=0.0, pts5=1.0,
            gf10=0.0, ga10=0.0, pts10=1.0
        )

    def gf(row):
        return row["HomeGoals"] if row["HomeTeam"] == team else row["AwayGoals"]

    def ga(row):
        return row["AwayGoals"] if row["HomeTeam"] == team else row["HomeGoals"]

    last5["gf"] = last5.apply(gf, axis=1)
    last5["ga"] = last5.apply(ga, axis=1)
    last10["gf"] = last10.apply(gf, axis=1)
    last10["ga"] = last10.apply(ga, axis=1)

    pts5 = last5.apply(
        lambda r: 3 if r["gf"] > r["ga"] else (1 if r["gf"] == r["ga"] else 0),
        axis=1
    ).mean()
    pts10 = last10.apply(
        lambda r: 3 if r["gf"] > r["ga"] else (1 if r["gf"] == r["ga"] else 0),
        axis=1
    ).mean()

    return dict(
        gf5=last5["gf"].mean(),
        ga5=last5["ga"].mean(),
        pts5=pts5,
        gf10=last10["gf"].mean(),
        ga10=last10["ga"].mean(),
        pts10=pts10,
    )


# ============================================================
# ELO RATING
# ============================================================

def get_elo(df, team, date):
    past = get_last_matches(df, team, date, 1)
    if past.empty:
        return 1500.0
    row = past.iloc[0]
    return float(row["elo_home"] if row["HomeTeam"] == team else row["elo_away"])


# ============================================================
# SEASONAL WINRATE
# ============================================================

def get_season(year, month):
    return f"{year-1}/{year}" if month < 7 else f"{year}/{year+1}"


def seasonal_stats(df, team, date):
    y = date.year
    season = get_season(y, date.month)

    tmp = df[
        ((df["HomeTeam"] == team) | (df["AwayTeam"] == team))
        & (df["Season"] == season)
        & (df["Date"] < date)
    ].copy()

    if tmp.empty:
        return dict(winrate=0.33, gf=1.2, ga=1.2)

    def gf(row):
        return row["HomeGoals"] if row["HomeTeam"] == team else row["AwayGoals"]

    def ga(row):
        return row["AwayGoals"] if row["HomeTeam"] == team else row["HomeGoals"]

    tmp["gf"] = tmp.apply(gf, axis=1)
    tmp["ga"] = tmp.apply(ga, axis=1)

    return dict(
        winrate=(tmp["gf"] > tmp["ga"]).mean(),
        gf=tmp["gf"].mean(),
        ga=tmp["ga"].mean(),
    )


# ============================================================
# LINEUP STRENGTH (proxy)
# ============================================================

def lineup_strength(team: str, date):
    """
    Estimation simple de la force de la compo:
    - basé sur forme récente + buts + Elo
    - s’appuie sur le dataset processed historique
    """
    base = 70.0  # neutre

    try:
        df_hist = pd.read_csv(
            PROCESSED / "all_matches_features.csv",
            parse_dates=["Date"],
            low_memory=False
        )

        df_team = df_hist[
            ((df_hist["HomeTeam"] == team) | (df_hist["AwayTeam"] == team))
            & (df_hist["Date"] < pd.to_datetime(date))
        ].sort_values("Date", ascending=False).head(1)

        if df_team.empty:
            return base

        last = df_team.iloc[0]

        if last["HomeTeam"] == team:
            atk = last.get("home_gf_avg_last_5", 1.2)
            defn = last.get("home_ga_avg_last_5", 1.0)
            elo = last.get("elo_home", 1500.0)
        else:
            atk = last.get("away_gf_avg_last_5", 1.2)
            defn = last.get("away_ga_avg_last_5", 1.0)
            elo = last.get("elo_away", 1500.0)

        strength = base + atk * 5 - defn * 3 + (elo - 1500.0) / 30.0
        return float(strength)

    except Exception:
        return base


# ============================================================
# STRENGTH OF SCHEDULE (ELO OPPONENTS)
# ============================================================

def last_opponents(df, team, date, n=5):
    tmp = get_last_matches(df, team, date, n)
    opps = []
    for _, r in tmp.iterrows():
        if r["HomeTeam"] == team:
            opps.append(r["AwayTeam"])
        else:
            opps.append(r["HomeTeam"])
    return opps


def sos(df, team, date):
    opps = last_opponents(df, team, date, 5)
    if len(opps) == 0:
        return 1500.0
    return float(np.mean([get_elo(df, o, date) for o in opps]))


# ============================================================
# PERFORMANCE VS TOP / BOTTOM
# ============================================================

def vs_group(df, team, date, group="top"):
    past = get_last_matches(df, team, date, 10)
    if past.empty:
        return 0.33

    wins = 0
    total = 0

    for _, r in past.iterrows():
        if r["HomeTeam"] == team:
            opp = r["AwayTeam"]
            gf = r["HomeGoals"]
            ga = r["AwayGoals"]
        else:
            opp = r["HomeTeam"]
            gf = r["AwayGoals"]
            ga = r["HomeGoals"]

        opp_elo = get_elo(df, opp, r["Date"])

        if group == "top" and opp_elo >= 1650:
            wins += (gf > ga)
            total += 1
        elif group == "bottom" and opp_elo <= 1400:
            wins += (gf > ga)
            total += 1

    return wins / total if total > 0 else 0.33


# ============================================================
# MOMENTUM
# ============================================================

def momentum(df, team, date):
    last5 = get_last_matches(df, team, date, 5)
    if last5.empty:
        return 0.0

    wins = 0
    goal_diff = 0

    for _, r in last5.iterrows():
        if r["HomeTeam"] == team:
            gd = r["HomeGoals"] - r["AwayGoals"]
        else:
            gd = r["AwayGoals"] - r["HomeGoals"]

        if gd > 0:
            wins += 1

        goal_diff += gd

    elo_now = get_elo(df, team, date)
    past_date = last5["Date"].min()
    elo_then = get_elo(df, team, past_date)
    elo_delta = elo_now - elo_then

    return wins * 0.6 + goal_diff * 0.3 + (elo_delta / 40.0) * 0.1


# ============================================================
# MARKET ODDS MOVEMENT (optionnel)
# ============================================================

def odds_movement(df, r):
    try:
        ph, pd, pa = compute_market_probabilities(r["OddsH"], r["OddsD"], r["OddsA"])
    except Exception:
        return 0.0, 0.0, 0.0

    # Ces colonnes doivent exister dans df pour que ça ait du sens.
    if not all(c in df.columns for c in ["pH_now", "pD_now", "pA_now"]):
        return 0.0, 0.0, 0.0

    rollH = df["pH_now"].rolling(5, min_periods=1).mean()
    rollD = df["pD_now"].rolling(5, min_periods=1).mean()
    rollA = df["pA_now"].rolling(5, min_periods=1).mean()

    return ph - rollH.iloc[-1], pd - rollD.iloc[-1], pa - rollA.iloc[-1]


# ============================================================
# HOME ADVANTAGE DYNAMIQUE
# ============================================================

def home_adv(df, team, date):
    past = get_last_matches(df, team, date, 20)
    if past.empty:
        return 0.05

    home_games = past[past["HomeTeam"] == team]
    if home_games.empty:
        return 0.05

    winrate = (home_games["HomeGoals"] > home_games["AwayGoals"]).mean()
    return float(winrate - 0.33)


# ============================================================
# XG PROXY (simple)
# ============================================================

def xg_proxy(df, team, date):
    last10 = get_last_matches(df, team, date, 10)
    if last10.empty:
        return 1.3
    avg_gf = last10.apply(
        lambda r: r["HomeGoals"] if r["HomeTeam"] == team else r["AwayGoals"],
        axis=1
    ).mean()
    avg_ga = last10.apply(
        lambda r: r["AwayGoals"] if r["HomeTeam"] == team else r["HomeGoals"],
        axis=1
    ).mean()
    return avg_gf * 0.7 + avg_ga * 0.3


# ============================================================
# MASTER BUILDER FUNCTION
# ============================================================

def build_features(df):
    """
    df doit contenir au minimum :
    - Date (datetime)
    - HomeTeam, AwayTeam
    - HomeGoals, AwayGoals
    - elo_home, elo_away (si déjà calculés, sinon tu peux les ajouter ensuite)
    """
    all_feat = []

    for _, r in df.iterrows():
        home = r["HomeTeam"]
        away = r["AwayTeam"]
        date = r["Date"]

        # form
        fH = compute_form(df, home, date)
        fA = compute_form(df, away, date)

        # seasonal
        sH = seasonal_stats(df, home, date)
        sA = seasonal_stats(df, away, date)

        row = {
            "HomeTeam": home,
            "AwayTeam": away,
            "Date": date,

            # Elo
            "elo_home": get_elo(df, home, date),
            "elo_away": get_elo(df, away, date),

            # form home
            "home_gf5": fH["gf5"],
            "home_ga5": fH["ga5"],
            "home_pts5": fH["pts5"],
            "home_gf10": fH["gf10"],
            "home_ga10": fH["ga10"],
            "home_pts10": fH["pts10"],

            # form away
            "away_gf5": fA["gf5"],
            "away_ga5": fA["ga5"],
            "away_pts5": fA["pts5"],
            "away_gf10": fA["gf10"],
            "away_ga10": fA["ga10"],
            "away_pts10": fA["pts10"],

            # seasonal
            "home_winrate_season": sH["winrate"],
            "home_goals_for_avg_season": sH["gf"],
            "home_goals_against_avg_season": sH["ga"],
            "away_winrate_season": sA["winrate"],
            "away_goals_for_avg_season": sA["gf"],
            "away_goals_against_avg_season": sA["ga"],

            # h2h (remplis plus tard si besoin)
            "h2h_home_adv": 0.0,
            "h2h_away_adv": 0.0,

            # lineup strength
            "lineup_strength_home": lineup_strength(home, date),
            "lineup_strength_away": lineup_strength(away, date),

            # strength of schedule
            "sos_home_last5": sos(df, home, date),
            "sos_away_last5": sos(df, away, date),

            # vs top / bottom
            "home_vs_top6": vs_group(df, home, date, "top"),
            "home_vs_bottom6": vs_group(df, home, date, "bottom"),
            "away_vs_top6": vs_group(df, away, date, "top"),
            "away_vs_bottom6": vs_group(df, away, date, "bottom"),

            # momentum
            "momentum_home": momentum(df, home, date),
            "momentum_away": momentum(df, away, date),

            # home advantage
            "home_advantage": home_adv(df, home, date),

            # xG proxies
            "xg_home": xg_proxy(df, home, date),
            "xg_away": xg_proxy(df, away, date),
        }

        all_feat.append(row)

    return pd.DataFrame(all_feat)
