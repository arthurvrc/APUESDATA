# =============================================
# BUILD HISTORY FROM MULTIPLE CSVs (APUESDATA)
# =============================================
import pandas as pd
from pathlib import Path
from src.config import RAW, HISTORY

def build_history():
    csv_folder = RAW / "csv"
    output_file = HISTORY / "all_history.csv"

    print(f"📂 Loading CSV files from: {csv_folder}")

    files = list(csv_folder.glob("*.csv"))
    if not files:
        print("❌ Aucun fichier CSV trouvé dans /data/raw/csv")
        return

    all_rows = []

    for f in files:
        try:
            df = pd.read_csv(f)
        except Exception as e:
            print(f"⚠️ Erreur lecture {f.name} : {e}")
            continue

        # Normalisation colonnes attendues
        expected = ["Date", "HomeTeam", "AwayTeam", "HomeGoals", "AwayGoals"]

        missing = [c for c in expected if c not in df.columns]
        if missing:
            print(f"⚠️ {f.name} ignoré : colonnes manquantes = {missing}")
            continue

        print(f"✔️ Loaded {f.name} ({df.shape[0]} rows)")
        all_rows.append(df[expected])

    if not all_rows:
        print("❌ Aucun CSV valide lu.")
        return

    df_all = pd.concat(all_rows, ignore_index=True)

    df_all = df_all.drop_duplicates()
    df_all = df_all.sort_values("Date")

    output_file.parent.mkdir(parents=True, exist_ok=True)
    df_all.to_csv(output_file, index=False)

    print(f"\n💾 Fichier historique créé : {output_file}")
    print(f"➡️ Total lignes : {df_all.shape[0]}")
    return df_all


if __name__ == "__main__":
    build_history()
