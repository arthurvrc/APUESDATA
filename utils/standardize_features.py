# =========================================
# STANDARDIZE FEATURES – APUESDATA
# =========================================

import pandas as pd


def normalize_team_name(name: str):
    """Nettoyage standardisé des noms d’équipes"""
    if not isinstance(name, str):
        return ""
    return (
        name.lower()
        .replace(".", "")
        .replace("-", " ")
        .replace("_", " ")
        .strip()
    )


def standardize_history(df: pd.DataFrame):
    """
    Pré-normalisation du dataset historique avant feature engineering :
    - normalisation HomeTeam / AwayTeam
    - conversion datetimes
    """

    df = df.copy()

    # Nettoyage noms équipes
    if "HomeTeam" in df.columns:
        df["HomeTeam"] = df["HomeTeam"].astype(str).apply(normalize_team_name)

    if "AwayTeam" in df.columns:
        df["AwayTeam"] = df["AwayTeam"].astype(str).apply(normalize_team_name)

    # Dates
    for col in ["Date", "date", "fixture_date"]:
        if col in df.columns:
            df["Date"] = pd.to_datetime(df[col], errors="coerce")
            break

    df = df.sort_values("Date").reset_index(drop=True)

    return df
