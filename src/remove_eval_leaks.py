import json
from pathlib import Path

TRAIN_FILE = Path("data/eval/training_pool.jsonl")
REVIEW_FILE = Path(__file__).resolve().parent / "leak_review.jsonl"
OUTPUT_FILE = Path("data/eval/training_pool_leak_free.jsonl")


def main():
    decisions = {}

    with REVIEW_FILE.open(encoding="utf-8-sig") as file:
        for line in file:
            if line.strip():
                review = json.loads(line)
                decisions[review["train_id"]] = review["decision"]

    seen = set()
    kept = 0
    removed = 0

    with TRAIN_FILE.open(encoding="utf-8-sig") as source:
        with OUTPUT_FILE.open("w", encoding="utf-8") as output:
            for line in source:
                if not line.strip():
                    continue

                record = json.loads(line)
                doc_id = record["id"]

                if doc_id in seen:
                    raise ValueError(f"Duplicate ID: {doc_id}")
                seen.add(doc_id)

                if decisions.get(doc_id) == "remove":
                    removed += 1
                    continue

                output.write(json.dumps(record, ensure_ascii=False) + "\n")
                kept += 1

    missing = set(decisions) - seen
    if missing:
        OUTPUT_FILE.unlink(missing_ok=True)
        raise ValueError(f"Reviewed IDs not found: {sorted(missing)}")

    print("Leak removal completed!")
    print("Removed:", removed)
    print("Retained:", kept)


if __name__ == "__main__":
    main()