import pandas as pd
from pathlib import Path

from src.api.api_football import get_fixtures_season
from src.config import RAW_FIX


def fetch_fixtures_api(season: int = 2024, leagues: list = None):
    """
    Récupère toutes les fixtures d'une saison pour les ligues spécifiées.
    """
    if leagues is None:
        leagues = [39, 61, 140, 78]  # Premier League, Ligue 1, LaLiga, Bundesliga

    print(f"➡️ Fetching fixtures for season {season}…")

    all_rows = []

    for lg in leagues:
        print(f"   📅 League {lg}…")

        matches = get_fixtures_season(lg, season)

        for m in matches:
            fixture = m.get("fixture", {})
            league = m.get("league", {})
            teams = m.get("teams", {})
            goals = m.get("goals", {})

            all_rows.append({
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

    df = pd.DataFrame(all_rows).drop_duplicates(subset=["fixture_id"])
    RAW_FIX.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(RAW_FIX, index=False)

    print(f"✅ Saved {len(df)} fixtures → {RAW_FIX}")


if __name__ == "__main__":
    fetch_fixtures_api()
