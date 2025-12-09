import streamlit as st
import pandas as pd
from pathlib import Path
from src.ui_theme import apply_custom_theme, page_title

apply_custom_theme()
page_title("Value bets", "📊")

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"

BETS = PROCESSED / "bets_recommendations.csv"

st.title("💰 Value Bets – IA PRO")

@st.cache_data
def load_bets():
    if BETS.exists():
        df = pd.read_csv(BETS)
        df["Date"] = pd.to_datetime(df["Date"])
        return df.sort_values("Date")
    return pd.DataFrame()

df = load_bets()

if df.empty:
    st.info("Aucun value bet disponible pour le moment.")
    st.stop()

st.write("""
Chaque ligne correspond à **un pari rentable détecté par l’IA**, basé sur :
- l’espérance de gain (EV),
- l’edge IA vs marché,
- la meilleure cote disponible,
- la calibration du modèle.
""")

st.dataframe(df, use_container_width=True)
