import requests
import time
from datetime import datetime, timedelta

from src.config import API_FOOTBALL_KEY, API_FOOTBALL_HOST

# ============================================================
# HEADERS API-FOOTBALL
# ============================================================

HEADERS = {
    "x-rapidapi-key": API_FOOTBALL_KEY,
    "x-rapidapi-host": API_FOOTBALL_HOST,
}


# ============================================================
# FONCTION GENERIQUE — Fetch un endpoint API-Football
# ============================================================

def fetch(endpoint: str, params: dict, retries: int = 3, sleep_time: int = 1):
    """
    Appel générique API avec retries et gestion du quota.
    Retourne [] si erreur / quota exceeded.
    """

    url = f"https://{API_FOOTBALL_HOST}/{endpoint}"

    for attempt in range(1, retries + 1):
        try:
            r = requests.get(url, params=params, headers=HEADERS, timeout=10)

            if r.status_code == 200:
                data = r.json()
                # Format API-Football = {"response": [...]}
                return data.get("response", [])

            elif r.status_code == 429:
                print(f"⚠️ Quota exceeded (attempt {attempt}/{retries}). Waiting…")
                time.sleep(sleep_time * attempt)
            
            else:
                print(f"❌ API Error {r.status_code}: {r.text}")
                return []

        except Exception as e:
            print(f"❌ Exception during API call: {e}")
            time.sleep(sleep_time * attempt)

    return []


# ============================================================
# FETCH FIXTURES PAR DATE (utilisé pour upcoming)
# ============================================================

def get_fixtures_by_date(date_str: str):
    """
    Récupère les fixtures d'une date YYYY-MM-DD.
    """
    return fetch(
        "v3/fixtures",
        {"date": date_str}
    )


# ============================================================
# UPCOMING sur X jours (7 par défaut)
# ============================================================

def get_upcoming_range(days: int = 7):
    """
    Récupère tous les matchs des X prochains jours.
    Utilisé par fetch_upcoming_api.
    """
    fixtures = []
    today = datetime.utcnow().date()

    for i in range(days):
        d = today + timedelta(days=i)
        d_str = d.strftime("%Y-%m-%d")

        print(f"   📅 Fetching date: {d_str}")
        day_matches = get_fixtures_by_date(d_str)

        if isinstance(day_matches, list):
            fixtures.extend(day_matches)
        else:
            print(f"⚠️ Erreur format API pour {d_str}")

    return fixtures


# ============================================================
# LAST FIXTURES (résultats récents)
# ============================================================

def get_last_fixtures(days_back: int = 3):
    """
    Récupère les résultats des 3 derniers jours.
    """
    fixtures = []
    today = datetime.utcnow().date()

    for i in range(days_back):
        d = today - timedelta(days=i+1)
        d_str = d.strftime("%Y-%m-%d")

        data = fetch(
            "v3/fixtures",
            {"date": d_str}
        )

        if isinstance(data, list):
            fixtures.extend(data)

    return fixtures
