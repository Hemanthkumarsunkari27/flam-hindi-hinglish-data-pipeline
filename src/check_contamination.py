
import json
import unicodedata
from pathlib import Path

EVAL_FILE = Path("data/eval/eval.jsonl")
TRAIN_FILE = Path("data/eval/training_pool.jsonl")
OUTPUT_FILE = Path("data/eval/contamination.jsonl")


def normalize_for_comparison(text):
    text = unicodedata.normalize("NFC", text)
    text = text.replace("\u200b", "").replace("\ufeff", "")
    return " ".join(text.split()).strip()


# Build lookup tables from the training pool.
exact_lookup = {}
normalized_lookup = {}

with TRAIN_FILE.open("r", encoding="utf-8") as file:
    for line in file:
        try:
            record = json.loads(line)
            text = record["text"]

            exact_lookup.setdefault(text, record["id"])

            normalized = normalize_for_comparison(text)
            normalized_lookup.setdefault(normalized, record["id"])

        except (json.JSONDecodeError, KeyError):
            continue

# Compare every evaluation document against training.
matches = []

with EVAL_FILE.open("r", encoding="utf-8") as file:
    for line in file:
        try:
            record = json.loads(line)
            text = record["text"]

            if text in exact_lookup:
                matches.append({
                    "eval_id": record["id"],
                    "train_id": exact_lookup[text],
                    "match_type": "exact"
                })

            else:
                normalized = normalize_for_comparison(text)

                if normalized in normalized_lookup:
                    matches.append({
                        "eval_id": record["id"],
                        "train_id": normalized_lookup[normalized],
                        "match_type": "normalized_exact"
                    })

        except (json.JSONDecodeError, KeyError):
            continue

# Save the results.
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

with OUTPUT_FILE.open("w", encoding="utf-8") as file:
    for match in matches:
        file.write(json.dumps(match, ensure_ascii=False) + "\n")

exact_count = sum(m["match_type"] == "exact" for m in matches)
normalized_count = sum(
    m["match_type"] == "normalized_exact" for m in matches
)

print("Contamination check completed!")
print("Evaluation documents checked: 200")
print("Exact matches:", exact_count)
print("Normalized exact matches:", normalized_count)
print("Total matches:", len(matches))
print("Report:", OUTPUT_FILE)
