import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"

RAW_FIX = RAW / "fixtures_api.csv"
RAW_RES = RAW / "results_api.csv"
HIST = PROCESSED / "all_matches_raw.csv"


def update_processed_data():
    """
    Met à jour all_matches_raw.csv en ajoutant fixtures_api + results_api.
    """

    print("⚙️ Mise à jour du dataset processed (all_matches_raw.csv)…")

    # === Lire historique ===
    if HIST.exists():
        df_old = pd.read_csv(HIST, low_memory=False)
    else:
        df_old = pd.DataFrame()

    # === Fixtures ===
    try:
        df_fix = pd.read_csv(RAW_FIX, parse_dates=["Date"], low_memory=False)
    except Exception:
        print("⚠️ Impossible de lire fixtures_api.csv → ignoré")
        df_fix = pd.DataFrame()

    # === Results ===
    try:
        df_res = pd.read_csv(RAW_RES, parse_dates=["Date"], low_memory=False)
    except Exception:
        print("⚠️ Impossible de lire results_api.csv → ignoré")
        df_res = pd.DataFrame()

    # === Fusionner ===
    df_new = pd.concat([df_old, df_fix, df_res], ignore_index=True)

    if df_new.empty:
        raise ValueError("⚠️ Processed vide → arrêt des features & training")

    # === Trier correctement ===
    if "Date" in df_new.columns:

        # 1️⃣ Convertir toutes les dates, même celles foireuses, en NaT
        df_new["Date"] = pd.to_datetime(df_new["Date"], errors="coerce", utc=True)

        # 2️⃣ Supprimer timezone pour tout uniformiser
        df_new["Date"] = df_new["Date"].dt.tz_convert(None)

        # 3️⃣ Trier proprement
        df_new = df_new.sort_values("Date").reset_index(drop=True)



    # === Sauvegarde ===
    PROCESSED.mkdir(parents=True, exist_ok=True)
    df_new.to_csv(HIST, index=False, encoding="utf-8-sig")

    print(f"✔️ all_matches_raw.csv mis à jour : {df_new.shape}")


if __name__ == "__main__":
    update_processed_data()
