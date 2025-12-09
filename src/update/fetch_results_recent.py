import requests
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from src.config import API_FOOTBALL_KEY

OUTPUT = Path("data/results_api.csv")

def fetch_results_recent():
    today = datetime.utcnow().date()
    from_date = today - timedelta(days=10)

    url = "https://v3.football.api-sports.io/fixtures"
    params = {
        "from": str(from_date),
        "to": str(today),
        "status": "FT"
    }
    headers = {"x-apisports-key": API_FOOTBALL_KEY}

    r = requests.get(url, headers=headers, params=params)
    r.raise_for_status()

    data = r.json().get("response", [])
    rows = []

    for m in data:
        fixture = m["fixture"]
        home = m["teams"]["home"]
        away = m["teams"]["away"]
        goals = m["goals"]

        rows.append({
            "fixture_id": fixture["id"],
            "date": fixture["date"],
            "home_name": home["name"],
            "away_name": away["name"],
            "home_goals": goals["home"],
            "away_goals": goals["away"]
        })

    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT, index=False)

    print(f"✔ Fetched {len(df)} results → {OUTPUT}")
    return df

if __name__ == "__main__":
    fetch_results_recent()
