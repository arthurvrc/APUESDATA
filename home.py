import streamlit as st

st.set_page_config(page_title="APUESDATA – IA Football", page_icon="⚽", layout="wide")

st.title("⚽ APUESDATA – IA Football")

st.markdown("""
Bienvenue dans **APUESDATA**, ton assistant IA intelligent pour analyser les matchs,
lire les probabilités avancées et détecter les **value bets** rentables.

---

## 🚀 Que peux-tu faire ici ?

### 📅 1) Explorer les matchs à venir
Analyse les matchs des **7 prochains jours**, classés par date et compétition.

### 🎯 2) Lire les prédictions IA complètes
Pour chaque match :
- Probabilités Home / Draw / Away  
- Explication claire  
- Visualisation graphique  

### 🔍 3) Analyser un match en détail
Avec :
- ELO des équipes  
- Forme  
- Stats 5 & 10 derniers matchs  
- Odds moyennes du marché  

### 💰 4) Identifier les value bets
Le modèle détecte automatiquement :
- Edge positif  
- EV > 0  
- Kelly optimal  

### 🔧 5) Mettre à jour les données
Via ton pipeline complet.

---

Utilise le menu en haut à gauche pour naviguer 🧭
""")
