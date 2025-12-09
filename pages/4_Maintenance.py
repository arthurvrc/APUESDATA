import streamlit as st
import subprocess
from src.ui_theme import apply_custom_theme, page_title

apply_custom_theme()
page_title("Maintenance", "📊")

st.title("⚙️ Maintenance & Mise à jour")

st.write("""
Cette page permet de **mettre à jour automatiquement** :
- les prochains matchs via API-Football,
- l’historique des résultats,
- les features PRO,
- les probabilités IA calibrées,
- les value bets.
""")

if st.button("🚀 Lancer la mise à jour complète (pipeline)"):
    with st.spinner("Mise à jour en cours…"):
        result = subprocess.run(["python", "-m", "src.update.full_update_pipeline"], capture_output=True, text=True)
        st.code(result.stdout)
    st.success("Mise à jour terminée !")
