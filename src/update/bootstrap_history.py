import pandas as pd
from pathlib import Path

from src.config import RAW, RAW_FIX, RAW_RES

def bootstrap_history():
    history_file = RAW / "history" / "history.csv"

    if not history_file.exists():
        print("❌ history.csv not found.")
        return

    df = pd.read_csv(history_file)

    # Standard columns
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    # Fixtures file (everything)
    df.to_csv(RAW_FIX, index=False)
    
    # Results (only matches where scores exist)
    results = df[df["HomeGoals"].notna() & df["AwayGoals"].notna()]
    results.to_csv(RAW_RES, index=False)

    print(f"✔ fixtures_api.csv created → {RAW_FIX}")
    print(f"✔ results_api.csv created → {RAW_RES}")
    print("🎉 History bootstrap completed.")

if __name__ == "__main__":
    bootstrap_history()
