import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta

from src.api.api_football import get_last_fixtures
from src.config import RAW_RES


def fetch_results_api(days_back: int = 3):
    """
    Récupère les matchs terminés sur les X derniers jours.
    Sauvegarde → data/raw/results_api.csv
    """
    print(f"➡️ Fetching results for last {days_back} days…")

    matches = get_last_fixtures(days_back)

    if not matches:
        print("⚠️ Aucun résultat récupéré")
        RAW_RES.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame().to_csv(RAW_RES, index=False)
        return

    rows = []
    for m in matches:
        fixture = m.get("fixture", {})
        league = m.get("league", {})
        teams = m.get("teams", {})
        goals = m.get("goals", {})

        rows.append({
            "fixture_id": fixture.get("id"),
            "date": fixture.get("date"),
            "league_id": league.get("id"),
            "season": league.get("season"),
            "HomeTeam": teams.get("home", {}).get("name", "").lower(),
            "AwayTeam": teams.get("away", {}).get("name", "").lower(),
            "HomeGoals": goals.get("home"),
            "AwayGoals": goals.get("away"),
            "status": fixture.get("status", {}).get("short")
        })

    df = pd.DataFrame(rows).drop_duplicates(subset=["fixture_id"])
    RAW_RES.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(RAW_RES, index=False)

    print(f"✅ Saved {len(df)} recent results → {RAW_RES}")


if __name__ == "__main__":
    fetch_results_api()
