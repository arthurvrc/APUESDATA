import requests
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from src.config import API_FOOTBALL_KEY

OUTPUT = Path("data/upcoming_api.csv")

def fetch_next_7_days():
    print("🔍 Fetching all fixtures for the next 7 days...")

    today = datetime.utcnow().date()
    end = today + timedelta(days=7)

    url = "https://v3.football.api-sports.io/fixtures"

    headers = {"x-apisports-key": API_FOOTBALL_KEY}

    params = {
        "from": today.strftime("%Y-%m-%d"),
        "to": end.strftime("%Y-%m-%d"),
        "status": "NS"  # Only upcoming matches
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        raise Exception(f"❌ API error {response.status_code}: {response.text}")

    data = response.json().get("response", [])
    print(f"📥 Fixtures received: {len(data)}")

    rows = []
    for f in data:
        fixture = f.get("fixture", {})
        league = f.get("league", {})
        teams = f.get("teams", {})

        rows.append({
            "fixture_id": fixture.get("id"),
            "date": fixture.get("date"),
            "league_id": league.get("id"),
            "season": league.get("season"),
            "home_name": teams.get("home", {}).get("name"),
            "away_name": teams.get("away", {}).get("name"),
            "home_id": teams.get("home", {}).get("id"),
            "away_id": teams.get("away", {}).get("id"),
            "status": fixture.get("status", {}).get("short")
        })

    df = pd.DataFrame(rows)

    # Clean date → datetime
    df["date"] = pd.to_datetime(df["date"], errors="coerce", utc=True)
    df["date"] = df["date"].dt.tz_convert(None)

    # Sort chronologically
    df = df.sort_values("date").reset_index(drop=True)

    # Save output
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT, index=False)

    print(f"💾 Saved to {OUTPUT} ({df.shape[0]} matches)")
    print("✔ Fetch next 7 days OK")

    return df


if __name__ == "__main__":
    fetch_next_7_days()
