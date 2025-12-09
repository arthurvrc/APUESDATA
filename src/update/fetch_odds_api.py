import pandas as pd
from src.api.api_football import _request

def fetch_odds_for_fixtures(fixture_ids):
    """
    Récupère les cotes moyennes (1X2) via API-Football pour une liste de fixtures.
    Retourne un DataFrame avec :
      fixture_id, odds_home_mean, odds_draw_mean, odds_away_mean
    """

    rows = []

    for fid in fixture_ids:
        data = _request("odds", {"fixture": fid})

        if not data:
            rows.append({
                "fixture_id": fid,
                "odds_home_mean": None,
                "odds_draw_mean": None,
                "odds_away_mean": None
            })
            continue

        # API-Football return structure
        bookmakers = data[0].get("bookmakers", [])

        all_H, all_D, all_A = [], [], []

        for book in bookmakers:
            bets = book.get("bets", [])
            for bet in bets:
                if bet.get("name") == "Match Winner":
                    for v in bet.get("values", []):
                        if v["value"] == "Home":
                            all_H.append(float(v["odd"]))
                        elif v["value"] == "Draw":
                            all_D.append(float(v["odd"]))
                        elif v["value"] == "Away":
                            all_A.append(float(v["odd"]))

        rows.append({
            "fixture_id": fid,
            "odds_home_mean": sum(all_H)/len(all_H) if all_H else None,
            "odds_draw_mean": sum(all_D)/len(all_D) if all_D else None,
            "odds_away_mean": sum(all_A)/len(all_A) if all_A else None,
        })

    return pd.DataFrame(rows)
