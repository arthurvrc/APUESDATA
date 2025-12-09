import streamlit as st
import pandas as pd
from pathlib import Path
from src.ui_theme import apply_custom_theme, page_title

apply_custom_theme()
page_title("Analyse du match", "📊")

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"

UPCOMING = PROCESSED / "predictions_upcoming.csv"

st.title("🧠 Analyse détaillée du Match")

@st.cache_data
def load_data():
    if UPCOMING.exists():
        df = pd.read_csv(UPCOMING)
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df["match"] = df["HomeTeam"] + " vs " + df["AwayTeam"]
        return df
    return pd.DataFrame()

df = load_data()

if df.empty:
    st.info("Aucun match disponible. Lance le pipeline d’abord.")
    st.stop()

match = st.selectbox("Choisir un match :", df["match"])

row = df[df["match"] == match].iloc[0]

st.subheader(f"📌 {row['match']}")
st.write(f"Date : {row['Date']}  •  League ID : {row['league_id']}")

col1, col2, col3 = st.columns(3)
col1.metric("🏠 Home", f"{row['p_home']:.1f} %")
col2.metric("🤝 Draw", f"{row['p_draw']:.1f} %")
col3.metric("🚩 Away", f"{row['p_away']:.1f} %")

# Comparaison avec marché
if "odds_home_mean" in row and not pd.isna(row["odds_home_mean"]):
    st.subheader("📈 Comparaison IA vs Marché")

    df_comp = pd.DataFrame({
        "Issue": ["Home", "Draw", "Away"],
        "Proba IA (%)": [row["p_home"], row["p_draw"], row["p_away"]],
        "Cote moyenne": [row["odds_home_mean"], row["odds_draw_mean"], row["odds_away_mean"]],
    })

    df_comp["Proba marché (%)"] = 100 / df_comp["Cote moyenne"]
    df_comp["Edge IA - marché (%)"] = df_comp["Proba IA (%)"] - df_comp["Proba marché (%)"]
    df_comp["EV (espérance gain %)"] = (
        df_comp["Proba IA (%)"]/100 * df_comp["Cote moyenne"] - 1
    ) * 100

    st.dataframe(df_comp, use_container_width=True)

else:
    st.info("⚠️ Aucune cote disponible pour ce match. Je ne peux afficher que les probabilités IA.")
