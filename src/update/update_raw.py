import pandas as pd
from pathlib import Path

from src.update.fetch_fixtures_api import fetch_fixtures
from src.update.fetch_results_api import fetch_last_results

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
RAW_FIX = RAW / "fixtures_api.csv"
RAW_RES = RAW / "results_api.csv"

def update_raw_data():
    print("⚙️ Mise à jour RAW (API-Football)")

    fix = fetch_fixtures(7)
    fix.to_csv(RAW_FIX, index=False)
    print(f"✔ Fixtures mis à jour ({len(fix)} matchs)")

    res = fetch_last_results(5)
    res.to_csv(RAW_RES, index=False)
    print(f"✔ Résultats mis à jour ({len(res)} matchs)")
