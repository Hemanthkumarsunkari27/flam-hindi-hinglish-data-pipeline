
import json
from collections import Counter
from pathlib import Path

input_file = Path(
    "data/exact_deduplicated/exact_deduplicated.jsonl"
)

language_counts = Counter()
total = 0
sample = None

with input_file.open("r", encoding="utf-8") as file:
    for line in file:
        try:
            record = json.loads(line)
            language = record.get("lang", "missing")

            language_counts[language] += 1
            total += 1

            if sample is None:
                sample = record

        except json.JSONDecodeError:
            continue

print("Total documents:", total)
print("Language counts:", dict(language_counts))

if sample:
    print("Sample fields:", list(sample.keys()))
    print("Sample ID:", sample.get("id"))
