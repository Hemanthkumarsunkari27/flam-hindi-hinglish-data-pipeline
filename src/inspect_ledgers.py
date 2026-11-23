
import json
from pathlib import Path

folders = [
    Path("data/quality_filtered"),
    Path("data/pii_redacted"),
    Path("data/exact_deduplicated"),
]

for folder in folders:
    print("\nFOLDER:", folder)

    for path in folder.glob("*ledger.jsonl"):
        count = 0
        first_record = None

        with path.open("r", encoding="utf-8") as file:
            for line in file:
                try:
                    record = json.loads(line)
                    count += 1
                    if first_record is None:
                        first_record = record
                except json.JSONDecodeError:
                    continue

        print("\nFile:", path.name)
        print("Rows:", count)
        print("Fields:", list(first_record.keys()) if first_record else "Empty")
        print("Sample:", first_record)

