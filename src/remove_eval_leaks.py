import json
from pathlib import Path

TRAIN_FILE = Path("data/eval/training_pool.jsonl")
CANDIDATES_FILE = Path("data/eval/near_copy_contamination.jsonl")
REVIEW_FILE = Path(__file__).resolve().parent / "leak_review.jsonl"
OUTPUT_FILE = Path("data/eval/training_pool_leak_free.jsonl")


def load_jsonl(path):
    with path.open("r", encoding="utf-8-sig") as file:
        for line in file:
            if line.strip():
                yield json.loads(line)


def main():
    reviews = {}

    for review in load_jsonl(REVIEW_FILE):
        pair = (review["eval_id"], review["train_id"])
        decision = review["decision"]

        if decision not in {"keep", "remove"}:
            raise ValueError(f"Invalid decision: {decision}")

        if pair in reviews:
            raise ValueError(f"Duplicate review: {pair}")

        reviews[pair] = decision

    candidates = {
        (item["eval_id"], item["train_id"])
        for item in load_jsonl(CANDIDATES_FILE)
    }

    remove_ids = set()
    pending = 0

    for pair in candidates:
        decision = reviews.get(pair)

        if decision == "remove":
            remove_ids.add(pair[1])
        elif decision is None:
            pending += 1

    kept = 0
    removed = 0
    seen = set()
    temp_file = OUTPUT_FILE.with_suffix(".tmp")

    try:
        with TRAIN_FILE.open("r", encoding="utf-8-sig") as source:
            with temp_file.open("w", encoding="utf-8") as output:
                for line in source:
                    if not line.strip():
                        continue

                    record = json.loads(line)
                    doc_id = record["id"]

                    if doc_id in seen:
                        raise ValueError(f"Duplicate training ID: {doc_id}")

                    seen.add(doc_id)

                    if doc_id in remove_ids:
                        removed += 1
                        continue

                    output.write(
                        json.dumps(record, ensure_ascii=False) + "\n"
                    )
                    kept += 1

        missing = remove_ids - seen

        if missing:
            raise ValueError(
                f"Reviewed training IDs not found: {sorted(missing)}"
            )

        temp_file.replace(OUTPUT_FILE)

    except Exception:
        temp_file.unlink(missing_ok=True)
        raise

    stale = len(set(reviews) - candidates)

    print("Leak removal completed!")
    print("Training documents removed:", removed)
    print("Training documents retained:", kept)
    print("Unreviewed candidates:", pending)
    print("Old review decisions ignored:", stale)
    print("Final training pool:", OUTPUT_FILE)


if __name__ == "__main__":
    main()