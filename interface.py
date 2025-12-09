# interface.py
from __future__ import annotations

import streamlit as st
import pandas as pd

from utils.loader import load_predictions_upcoming, load_value_bets, filter_next_days

st.set_page_config(
    page_title="APUESDATA – Dashboard IA Football",
    page_icon="⚽",
    layout="wide",
)

# ========= CHARGEMENT DES DONNÉES =========
preds = load_predictions_upcoming()
bets = load_value_bets()
next7 = filter_next_days(preds, days=7)

# ========= SIDEBAR : recherche simple =========
with st.sidebar:
    st.markdown("### 🔍 Recherche équipe")
    search = st.text_input("Nom d’équipe ou mot-clé")

    if not next7.empty:
        df_search = next7.copy()
        if search:
            df_search = df_search[df_search["match"].str.contains(search, case=False, na=False)]

        match_list = ["Aucun"] + df_search["match"].tolist()
    else:
        match_list = ["Aucun"]

    selected_match = st.selectbox("Sélectionne un match :", match_list)


# ========= PAGE D’ACCUEIL =========
st.markdown("# ⚽ APUESDATA – Dashboard IA Football")
st.markdown(
    "Bienvenue ! Voici un résumé **des matchs à venir** avec leurs **probabilités IA** "
    "et les **value bets** détectés."
)

# ---------- Bloc 1 : Matchs à venir ----------
st.markdown("## 📅 Matchs à venir (7 jours)")

if next7.empty:
    st.info(
        "Aucun match avec prédictions n’est prévu dans les 7 prochains jours.\n\n"
        "➡︎ Lance d’abord la mise à jour dans l’onglet **Maintenance**."
    )
else:
    df_display = next7.copy()

    # Pourcentages lisibles
    df_display["P(Home)_%"] = (df_display["p_home"] * 100).round(1)
    df_display["P(Draw)_%"] = (df_display["p_draw"] * 100).round(1)
    df_display["P(Away)_%"] = (df_display["p_away"] * 100).round(1)

    cols_to_show = [
        "Date",
        "league_id",
        "match",
        "P(Home)_%",
        "P(Draw)_%",
        "P(Away)_%",
        "odds_home_mean",
        "odds_draw_mean",
        "odds_away_mean",
    ]
    cols_existing = [c for c in cols_to_show if c in df_display.columns]

    st.caption("💡 Clique sur l’en-tête d’une colonne pour **trier** (par proba, cote, date, ligue…).")
    st.dataframe(
        df_display[cols_existing],
        hide_index=True,
        use_container_width=True,
    )

# ---------- Bloc 2 : Résumé du match sélectionné ----------
st.markdown("## 🎯 Résumé rapide du match sélectionné")

if selected_match == "Aucun":
    st.info("Sélectionne un match dans le menu de gauche pour voir les probabilités et le conseil de pari.")
else:
    row_all = preds[preds["match"] == selected_match]
    if row_all.empty:
        st.warning("Aucune prédiction trouvée pour ce match. Relance la mise à jour dans l’onglet Maintenance.")
    else:
        r = row_all.iloc[0]

        p_home = float(r.get("p_home", 0.0))
        p_draw = float(r.get("p_draw", 0.0))
        p_away = float(r.get("p_away", 0.0))

        c1, c2, c3 = st.columns(3)
        c1.metric("🏠 Victoire Home", f"{p_home*100:.1f} %")
        c2.metric("🤝 Match nul", f"{p_draw*100:.1f} %")
        c3.metric("🚩 Victoire Away", f"{p_away*100:.1f} %")

        # Implied probs à partir des cotes (si dispo)
        oh = float(r.get("odds_home_mean", 0))
        od = float(r.get("odds_draw_mean", 0))
        oa = float(r.get("odds_away_mean", 0))

        if oh > 0 and od > 0 and oa > 0:
            inv_sum = (1 / oh) + (1 / od) + (1 / oa)
            fair_h = (1 / oh) / inv_sum
            fair_d = (1 / od) / inv_sum
            fair_a = (1 / oa) / inv_sum

            edge_h = p_home - fair_h
            edge_d = p_draw - fair_d
            edge_a = p_away - fair_a

            ev_h = oh * p_home - 1
            ev_d = od * p_draw - 1
            ev_a = oa * p_away - 1

            # Choisir le meilleur pari selon EV
            options = {
                "Home": ("🏠 Victoire Home", ev_h, edge_h, oh, p_home),
                "Draw": ("🤝 Match nul", ev_d, edge_d, od, p_draw),
                "Away": ("🚩 Victoire Away", ev_a, edge_a, oa, p_away),
            }
            best_key = max(options, key=lambda k: options[k][1])
            label, best_ev, best_edge, best_odds, best_p = options[best_key]

            st.markdown("### 💡 Conseil IA (basé sur les cotes actuelles)")
            if best_ev > 0 and best_edge > 0:
                st.success(
                    f"**{label}** semble le pari le plus intéressant.\n\n"
                    f"- Proba modèle ≈ **{best_p*100:.1f} %**\n"
                    f"- Cote ≈ **{best_odds:.2f}**\n"
                    f"- EV (espérance de gain) ≈ **{best_ev*100:.1f} %**\n"
                    f"- Edge (modèle vs marché) ≈ **{best_edge*100:.1f} %**"
                )
            else:
                st.info(
                    "D’après le modèle et les cotes actuelles, **aucun pari n’a un EV clairement positif**.\n\n"
                    "➡︎ Si tu veux tenter un pari, le plus « raisonnable » est simplement "
                    f"le résultat avec la proba IA la plus élevée (**{label}**)."
                )
        else:
            st.info(
                "Les cotes moyennes ne sont pas disponibles pour ce match.\n"
                "Je peux quand même te donner les probabilités IA, mais pas l’EV ni l’edge."
            )

# ---------- Bloc 3 : Value Bets rapides ----------
st.markdown("## 💰 Value Bets détectés (résumé)")

if bets.empty:
    st.info("Aucun value bet détecté pour l’instant. Relance la mise à jour dans l’onglet **Maintenance**.")
else:
    cols_to_show = [
        "Date",
        "HomeTeam",
        "AwayTeam",
        "best_outcome",
        "best_odds",
        "best_model_prob",
        "expected_value",
        "kelly_fraction",
    ]
    cols_existing = [c for c in cols_to_show if c in bets.columns]

    bets_sorted = bets.sort_values("expected_value", ascending=False).head(10)

    st.caption("Voici les **10 meilleurs value bets** détectés par le modèle (EV et Kelly les plus élevés).")
    st.dataframe(
        bets_sorted[cols_existing],
        hide_index=True,
        use_container_width=True,
    )

st.markdown("---")
st.caption(
    "🔧 Pour recalculer toutes les données (API + features + modèle + value bets), "
    "va dans l’onglet **Maintenance**."
)
