
import json
from pathlib import Path

TRAIN_FILE = Path("data/eval/training_pool.jsonl")
OUTPUT_FILE = Path("data/eval/training_pool_leak_free.jsonl")

# Four manually confirmed near-copy training documents.
LEAK_IDS = {
    "COMI_015962",
    "COMI_005888",
    "COMI_009985",
    "COMI_010125"
}

kept = 0
removed = 0

with TRAIN_FILE.open("r", encoding="utf-8") as source:
    with OUTPUT_FILE.open("w", encoding="utf-8") as output:
        for line in source:
            record = json.loads(line)

            if record["id"] in LEAK_IDS:
                removed += 1
                continue

            output.write(json.dumps(record, ensure_ascii=False) + "\n")
            kept += 1

print("Leak removal completed!")
print("Training documents removed:", removed)
print("Training documents retained:", kept)
print("Final training pool:", OUTPUT_FILE)
