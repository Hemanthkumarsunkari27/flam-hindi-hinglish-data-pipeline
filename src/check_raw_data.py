
import csv
from pathlib import Path

RAW_DIR = Path("data/raw")

FILES = [
    "LID_train.csv",
    "HinGE.csv"
]

for filename in FILES:
    path = RAW_DIR / filename

    print("\n" + "=" * 60)
    print("FILE:", filename)

    if not path.exists():
        print("ERROR: File not found!")
        continue

    print("Size:", round(path.stat().st_size / 1024, 2), "KB")

    try:
        with open(
            path,
            "r",
            encoding="utf-8-sig",
            newline=""
        ) as file:

            reader = csv.DictReader(file)

            print("Columns:", reader.fieldnames)

            count = 0

            for row in reader:
                count += 1

                # Display only the first two records
                if count <= 2:
                    print("\nSample", count)

                    for column, value in row.items():
                        print(
                            column,
                            ":",
                            str(value)[:250]
                        )

            print("\nTOTAL ROWS:", count)

    except Exception as error:
        print("ERROR:", error)

print("\nRaw dataset inspection completed!")