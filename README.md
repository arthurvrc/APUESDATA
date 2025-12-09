# ⚽ APUESDATA – AI Football Predictions Engine  
**Advanced Machine Learning System for Match Outcome Forecasting, Value Bets Detection & Betting Intelligence**

APUESDATA is a full-stack football prediction engine combining:
- 15+ years of historical match data  
- Automated ELO computation  
- Advanced feature engineering (47 high-performance features)  
- XGBoost Pro model with calibration  
- Real-time odds, fixtures & results via API-Football  
- Fully automated prediction pipeline  
- Interactive web interface (Streamlit)  
- Value bet detection & betting recommendations  

---

## 🚀 Features

### ✔ Machine Learning Engine
- XGBoost Pro model  
- Probability calibration  
- Predicts Home/Draw/Away outcomes  
- Logs, reports & evaluation tools  
- Achieves ~53% accuracy over 220,000 matches

### ✔ 47 Feature Inputs
Including:
- Advanced ELO  
- Form (last 5 / 10 games)  
- Goals for/against rolling stats  
- Over/Under/Btts rolling rates  
- Seasonal performance indicators  
- Market odds (Bet365, Pinnacle, BW, WH, VC, IW…)  

### ✔ Automated Data Pipeline
python -m src.update.full_update_pipeline
This fetches:
- Fixtures  
- Odds  
- Results  
- Builds features  
- Predicts all upcoming matches  
- Detects value bets  
- Generates recommendations  
- Updates dashboard  

### ✔ Streamlit UI
Run:
streamlit run interface.py

Pages included:
- Match predictions  
- Analysis per match  
- Value bets ranking  
- Maintenance & dev tools  

---

## 🧠 Model Performance

Latest evaluation (`evaluate_xgb_pro.py`):
- **Accuracy:** 52.89%  
- **Log Loss:** 0.952  
- **Dataset:** 220k+ matches  
- **Calibration:** Enabled  
- **Confusion matrix & report included**

---

## 📦 Project Structure
APUESDATA/
│ .gitignore
│ requirements.txt
│ run_all.py
│ home.py
│ interface.py
│ pages/
│ src/
│ utils/
│ data/fixtures/
│ models/ (excluded from git)
│ data/ (excluded from git)


---

## 📥 Installation
pip install -r requirements.txt

Create a `.env`:
API_FOOTBALL_KEY=your_api_key

---

## ▶ Run the app
streamlit run interface.py

Or full update:

python run_all.py

---

## 📊 Predicting upcoming matches
python -m src.update.build_upcoming_features_pro
python -m src.predict.predict_upcoming
python -m src.update.compute_value_bets
python -m src.update.analyze_predictions
---

## 🧪 Model Training
python -m src.model.train_xgb_pro

## 📏 Evaluation
python -m src.model.evaluate_xgb_pro

---

## 🔎 Value Bets Detection
Uses:
- Expected value  
- Edge calculation  
- Probability calibration  
- Odds comparison  

Outputs are saved in:
data/processed/match_recommendations.csv

---

## 🧱 Technologies
- Python 3.11  
- XGBoost  
- Pandas / NumPy  
- Scikit-learn  
- Streamlit  
- API-Football  
- Custom ELO engine  
- Automated pipeline architecture  

---

## 📘 License
Proprietary project — Do not distribute without owner consent.

