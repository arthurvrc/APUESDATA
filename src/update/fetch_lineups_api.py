import requests
import pandas as pd
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("FOOTBALL_DATA_API_KEY")
API_URL = "https://v3.football.api-sports.io/fixtures/lineups"

HEADERS = {
    "x-apisports-key": API_KEY
}

def fetch_lineups(fixture_ids):
    """Retourne les lineups pour une liste de fixtures."""
    rows = []
    for fid in fixture_ids:
        url = f"{API_URL}?fixture={fid}"
        r = requests.get(url, headers=HEADERS)
        data = r.json()

        if "response" not in data or len(data["response"]) == 0:
            continue

        home = data["response"][0].get("startXI", [])
        away = data["response"][1].get("startXI", [])

        rows.append({
            "MatchID_API": fid,
            "home_lineup": ";".join([p["player"]["name"] for p in home]),
            "away_lineup": ";".join([p["player"]["name"] for p in away]),
            "home_rating": sum([p["player"].get("rating", 6.5) for p in home]) / len(home) if home else 6.5,
            "away_rating": sum([p["player"].get("rating", 6.5) for p in away]) / len(away) if away else 6.5,
        })

    return pd.DataFrame(rows)
