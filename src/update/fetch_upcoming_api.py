import pandas as pd
from pathlib import Path

from src.api.api_football import get_upcoming_range
from src.config import UPCOMING, RAW

# ===================================================================
# FETCH UPCOMING FIXTURES — 7 jours, version PRO
# ===================================================================

def fetch_upcoming_api(days: int = 7):
    print("➡️ Fetching upcoming fixtures (date endpoint)…")

    matches = get_upcoming_range(days)

    if not matches:
        print("⚠️ Aucun match trouvé via API-Football")
        UPCOMING.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame().to_csv(UPCOMING, index=False)
        print("✔ Script fetch_upcoming_api exécuté")
        return

    rows = []
    for m in matches:
        fixture = m.get("fixture", {})
        league = m.get("league", {})
        teams = m.get("teams", {})

        rows.append({
            "fixture_id": fixture.get("id"),
            "date": fixture.get("date"),
            "league_id": league.get("id"),
            "season": league.get("season"),
            "home_name": teams.get("home", {}).get("name", "").lower(),
            "away_name": teams.get("away", {}).get("name", "").lower(),
            "home_id": teams.get("home", {}).get("id"),
            "away_id": teams.get("away", {}).get("id"),
            "status": fixture.get("status", {}).get("short")
        })

    df = pd.DataFrame(rows).drop_duplicates(subset=["fixture_id"])

    UPCOMING.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(UPCOMING, index=False)

    print(f"✅ Saved {len(df)} matches → {UPCOMING}")
    print("✔ fetch_upcoming_api finished.")


if __name__ == "__main__":
    fetch_upcoming_api()
