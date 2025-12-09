# =========================================
# FULL UPDATE PIPELINE – APUESDATA PRO
# =========================================

from src.update.fetch_upcoming_api import fetch_upcoming_api
from src.update.update_history import update_history
from src.update.rebuild_features_pro import rebuild_all_features
from src.update.build_upcoming_features_pro import build_upcoming_features_pro
from src.update.predict_upcoming import predict_upcoming
from src.update.compute_value_bets import compute_value_bets

def safe_run(title, func):
    print(f"\n🔧 Étape : {title}")
    try:
        func()
        print(f"✔️ {title} OK")
    except Exception as e:
        print(f"❌ ERREUR dans {title} : {e}")
        raise e

def main():
    print("🚀 APUESDATA – FULL UPDATE PIPELINE (PRO)\n")

    safe_run("Fetch upcoming fixtures (API-Football)", fetch_upcoming_api)
    safe_run("Update RAW (fixtures + results)", update_history)
    safe_run("Rebuild PRO features (historical)", rebuild_all_features)
    safe_run("Build upcoming PRO features", build_upcoming_features_pro)
    safe_run("Predict upcoming fixtures (XGB + calibration)", predict_upcoming)
    safe_run("Compute value bets (EV + Kelly)", compute_value_bets)

    print("\n🎉 Pipeline complet terminé !")

if __name__ == "__main__":
    main()
