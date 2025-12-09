# =========================================
# UPDATE HISTORY – APUESDATA PRO
# =========================================

import pandas as pd
from pathlib import Path
from src.config import RAW_FIX, RAW_RES, RAW_LAST_RES, HISTORY

def safe_read_csv(path: Path):
    """Load CSV safely: returns empty DF if file missing or empty."""
    try:
        if path.exists() and path.stat().st_size > 0:
            return pd.read_csv(path)
        return pd.DataFrame()
    except:
        return pd.DataFrame()

def update_history():
    print("🔧 Loading RAW history files...")

    df_fix = safe_read_csv(RAW_FIX)
    df_res = safe_read_csv(RAW_RES)
    df_last = safe_read_csv(RAW_LAST_RES)

    if df_fix.empty and df_res.empty and df_last.empty:
        print("⚠️ Aucun historique disponible")
        return

    # Harmonisation colonnes
    rename_map = {
        "home_name": "HomeTeam",
        "away_name": "AwayTeam",
        "home_goals": "HomeGoals",
        "away_goals": "AwayGoals",
        "date": "Date",
    }

    def normalize(df):
        df = df.rename(columns=rename_map)
        if "HomeTeam" in df.columns:
            df["HomeTeam"] = df["HomeTeam"].astype(str).str.lower()
        if "AwayTeam" in df.columns:
            df["AwayTeam"] = df["AwayTeam"].astype(str).str.lower()
        return df

    df_fix = normalize(df_fix)
    df_res = normalize(df_res)
    df_last = normalize(df_last)

    # -------------------------
    # Combine all match records
    # -------------------------
    df_all = pd.concat([df_fix, df_res, df_last], ignore_index=True)

    # Remove duplicates
    if "fixture_id" in df_all.columns:
        df_all = df_all.drop_duplicates(subset=["fixture_id"], keep="last")

    # Save into history folder
    HISTORY.mkdir(parents=True, exist_ok=True)
    out = HISTORY / "all_history.csv"

    df_all.to_csv(out, index=False)
    print(f"💾 Saved history → {out} (shape={df_all.shape})")

    return df_all


if __name__ == "__main__":
    update_history()
