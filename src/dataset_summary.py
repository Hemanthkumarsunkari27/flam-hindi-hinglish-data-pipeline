
import csv
from pathlib import Path

files = [
    "LID_train.csv",
    "HinGE.csv"
]

for filename in files:
    path = Path("data/raw") / filename

    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        count = sum(1 for _ in reader)

    print("-" * 40)
    print("Dataset:", filename)
    print("Rows:", count)
    print("Size:", round(path.stat().st_size / (1024 * 1024), 2), "MB")

print("\nInspection completed!")
