import os
import requests
from pathlib import Path
from dotenv import load_dotenv

# Charger .env
ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

API_KEY = os.getenv("API_FOOTBALL_KEY")
API_HOST = os.getenv("API_FOOTBALL_HOST")

BASE_URL = "https://api-football-v1.p.rapidapi.com/v3"

headers = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": API_HOST
}

def test_api():
    url = f"{BASE_URL}/fixtures"
    params = {
        "league": 39,    # Premier League
        "season": 2023   # saison au choix
    }

    r = requests.get(url, headers=headers, params=params)
    r.raise_for_status()   # lève une erreur si mauvaise clé

    data = r.json().get("response", [])
    print("Nombre de matchs récupérés :", len(data))

    # Affiche 3 matchs
    for f in data[:3]:
        date = f["fixture"]["date"]
        home = f["teams"]["home"]["name"]
        away = f["teams"]["away"]["name"]
        print(f"{date} | {home} vs {away}")

if __name__ == "__main__":
    test_api()
