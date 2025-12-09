import pandas as pd
from src.config import PROCESSED

def normalize_column(df, name_options):
    """Choisit la 1ère colonne existante parmi plusieurs noms possibles."""
    for n in name_options:
        if n in df.columns:
            return n
    return None


def analyze():
    df = pd.read_csv(PROCESSED / "predictions_upcoming.csv")

    # Detect column names dynamically
    col_home = normalize_column(df, ["HomeTeam", "home_team", "home"])
    col_away = normalize_column(df, ["AwayTeam", "away_team", "away"])
    col_fixture = normalize_column(df, ["fixture_id", "id", "match_id"])

    recs = []

    for _, r in df.iterrows():
        conf = max(r.p_home, r.p_draw, r.p_away)

        recs.append({
            "fixture_id": r.get(col_fixture, None),
            "HomeTeam": r.get(col_home, "unknown"),
            "AwayTeam": r.get(col_away, "unknown"),
            "Recommended": ["HOME", "DRAW", "AWAY"][ [r.p_home, r.p_draw, r.p_away].index(conf) ],
            "Confidence": round(conf, 3)
        })

    out = PROCESSED / "match_recommendations.csv"
    pd.DataFrame(recs).to_csv(out, index=False)
    print(f"💾 Saved → {out}")


if __name__ == "__main__":
    analyze()
