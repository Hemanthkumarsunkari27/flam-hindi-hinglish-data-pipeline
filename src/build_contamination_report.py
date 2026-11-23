
import json
from pathlib import Path

EVAL_FILE = Path("data/eval/eval.jsonl")
NEAR_FILE = Path("data/eval/near_copy_contamination.jsonl")
OUTPUT_FILE = Path("output/contamination.jsonl")

# Only the four manually confirmed leaks.
CONFIRMED_LEAKS = {
    "COMI_015962",
    "COMI_005888",
    "COMI_009985",
    "COMI_010125"
}

# Map each affected evaluation item to its confirmed training leak.
affected = {}

with NEAR_FILE.open("r", encoding="utf-8") as file:
    for line in file:
        record = json.loads(line)

        if record["train_id"] in CONFIRMED_LEAKS:
            eval_id = record["eval_id"]

            if eval_id not in affected:
                affected[eval_id] = {
                    "eval_id": eval_id,
                    "train_ids": [],
                    "method": "near_copy"
                }

            affected[eval_id]["train_ids"].append(record["train_id"])

# Save one row per affected evaluation item.
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

with OUTPUT_FILE.open("w", encoding="utf-8") as file:
    for eval_id in sorted(affected):
        record = affected[eval_id]
        record["train_ids"] = sorted(set(record["train_ids"]))
        file.write(json.dumps(record, ensure_ascii=False) + "\n")

print("Contamination report created!")
print("Affected evaluation items:", len(affected))
print("Confirmed training leaks:", len(CONFIRMED_LEAKS))
print("Output:", OUTPUT_FILE)
