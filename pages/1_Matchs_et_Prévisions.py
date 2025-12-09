import streamlit as st
import pandas as pd
from pathlib import Path
from src.ui_theme import apply_custom_theme, page_title

apply_custom_theme()
page_title("Matchs & Prévisions IA", "📊")

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
PROCESSED = DATA / "processed"

UPCOMING = PROCESSED / "predictions_upcoming.csv"

st.title("📊 Matchs & Prévisions IA")

st.write("""
Cette page montre **tous les matchs à venir** avec :
- les probabilités IA (Home / Draw / Away),
- les cotes moyennes,
- les prédictions calibrées,
- la possibilité de filtrer facilement par équipe ou ligue.
""")

@st.cache_data
def load_predictions():
    if UPCOMING.exists():
        df = pd.read_csv(UPCOMING)
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        return df.sort_values("Date")
    else:
        return pd.DataFrame()

df = load_predictions()

if df.empty:
    st.info("Aucun match disponible. Lance d'abord le pipeline dans l'onglet Maintenance.")
    st.stop()

# 🔍 Recherche équipe
team_filter = st.text_input("Rechercher une équipe, un match ou un mot-clé :").lower()

if team_filter:
    df = df[df.apply(lambda r: team_filter in str(r).lower(), axis=1)]

# 🗂 Tableau propre
display = df[[
    "Date",
    "HomeTeam",
    "AwayTeam",
    "league_id",
    "p_home",
    "p_draw",
    "p_away",
    "odds_home_mean",
    "odds_draw_mean",
    "odds_away_mean",
]]

display = display.rename(columns={
    "p_home": "P(Home) %",
    "p_draw": "P(Draw) %",
    "p_away": "P(Away) %",
})

st.dataframe(display, use_container_width=True)
