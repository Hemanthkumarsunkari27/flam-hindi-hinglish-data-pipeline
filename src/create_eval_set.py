
import json
import random
from collections import defaultdict
from pathlib import Path

INPUT_FILE = Path("data/exact_deduplicated/exact_deduplicated.jsonl")
EVAL_DIR = Path("data/eval")

EVAL_SIZE = 200
RANDOM_SEED = 42

random.seed(RANDOM_SEED)

# Read documents and group them by language.
groups = defaultdict(list)

with INPUT_FILE.open("r", encoding="utf-8") as file:
    for line in file:
        try:
            record = json.loads(line)
            groups[record["lang"]].append(record)
        except (json.JSONDecodeError, KeyError):
            continue

# Select a representative sample from each language.
targets = {
    "hi": 127,
    "hi-Latn": 50,
    "en": 23
}

selected_ids = set()
evaluation_records = []

for language, target_count in targets.items():
    available = groups.get(language, [])

    if len(available) < target_count:
        raise ValueError(f"Not enough documents for {language}")

    selected = random.sample(available, target_count)

    for record in selected:
        selected_ids.add(record["id"])
        evaluation_records.append(record)

# Keep the evaluation order reproducible.
evaluation_records.sort(key=lambda record: record["id"])

EVAL_DIR.mkdir(parents=True, exist_ok=True)

# Save evaluation documents.
with (EVAL_DIR / "eval.jsonl").open("w", encoding="utf-8") as file:
    for record in evaluation_records:
        file.write(json.dumps(record, ensure_ascii=False) + "\n")

# Save all remaining documents as the training pool.
training_count = 0

with (EVAL_DIR / "training_pool.jsonl").open("w", encoding="utf-8") as output:
    with INPUT_FILE.open("r", encoding="utf-8") as source:
        for line in source:
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue

            if record["id"] not in selected_ids:
                output.write(json.dumps(record, ensure_ascii=False) + "\n")
                training_count += 1

# Save evaluation details.
manifest = {
    "evaluation_size": len(evaluation_records),
    "training_pool_size": training_count,
    "random_seed": RANDOM_SEED,
    "language_counts": targets,
    "purpose": "Held-out audit set for language and data-quality review",
    "note": "Language labels are heuristic predictions, not manually verified gold labels."
}

with (EVAL_DIR / "eval_manifest.json").open("w", encoding="utf-8") as file:
    json.dump(manifest, file, ensure_ascii=False, indent=4)

print("Evaluation set created successfully!")
print("Evaluation documents:", len(evaluation_records))
print("Training pool documents:", training_count)
print("Language distribution:", targets)
print("Output folder:", EVAL_DIR)
