import subprocess
import sys

COMMANDS = [
    "python -m src.update.build_upcoming_features_pro",
    "python -m src.predict.predict_upcoming",
    "python -m src.update.compute_value_bets",
    "python -m src.update.analyze_predictions",
]

def run(cmd):
    print("\n🚀 Running:", cmd)
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"❌ ERROR during: {cmd}")
        sys.exit(1)
    print(f"✔ DONE: {cmd}")

if __name__ == "__main__":
    print("======================================")
    print("     APUESDATA – FULL DAILY UPDATE    ")
    print("======================================")

    for cmd in COMMANDS:
        run(cmd)

    print("\n🎉 ALL STEPS COMPLETED SUCCESSFULLY!")
