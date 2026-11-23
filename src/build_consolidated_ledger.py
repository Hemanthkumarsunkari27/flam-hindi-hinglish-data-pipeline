
import json
from pathlib import Path

QUALITY_FILE = Path("data/quality_filtered/quality_filter_ledger.jsonl")
EXACT_FILE = Path("data/exact_deduplicated/exact_deduplication_ledger.jsonl")
EVAL_FILE = Path("data/eval/eval.jsonl")
NEAR_FILE = Path("data/eval/near_copy_contamination.jsonl")
OUTPUT_FILE = Path("output/ledger.jsonl")

NEAR_COPY_LEAK_IDS = {
    "COMI_015962",
    "COMI_005888",
    "COMI_009985",
    "COMI_010125"
}


def load_ledger(path):
    records = {}
    with path.open("r", encoding="utf-8") as file:
        for line in file:
            record = json.loads(line)
            records[record["id"]] = record
    return records


quality = load_ledger(QUALITY_FILE)
exact = load_ledger(EXACT_FILE)

with EVAL_FILE.open("r", encoding="utf-8") as file:
    eval_ids = {json.loads(line)["id"] for line in file}

# Map each confirmed training leak to its affected evaluation document.
near_leak_map = {}

with NEAR_FILE.open("r", encoding="utf-8") as file:
    for line in file:
        record = json.loads(line)
        if record["train_id"] in NEAR_COPY_LEAK_IDS:
            near_leak_map[record["train_id"]] = record["eval_id"]

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

counts = {"kept": 0, "dropped": 0}

with OUTPUT_FILE.open("w", encoding="utf-8") as output:
    for doc_id, quality_record in quality.items():

        exact_record = exact.get(doc_id)
        dup_of = None

        if quality_record["status"] != "kept":
            status = "dropped"
            stage = "quality_filter"
            reason = quality_record["reason"]

        elif exact_record and exact_record["status"] != "kept":
            status = "dropped"
            stage = "exact_deduplication"
            reason = exact_record["reason"]
            dup_of = exact_record.get("dup_of")

        elif doc_id in near_leak_map:
            status = "dropped"
            stage = "evaluation_contamination"
            reason = "near_copy_leak"
            dup_of = near_leak_map[doc_id]

        elif doc_id in eval_ids:
            status = "dropped"
            stage = "evaluation_holdout"
            reason = "held_out_for_evaluation"

        else:
            status = "kept"
            stage = "final_dataset"
            reason = "included_in_training"

        row = {
            "id": doc_id,
            "status": status,
            "stage": stage,
            "reason": reason,
            "dup_of": dup_of
        }

        output.write(json.dumps(row, ensure_ascii=False) + "\n")
        counts[status] += 1

print("Consolidated ledger created!")
print("Total input documents:", len(quality))
print("Status counts:", counts)
print("Output:", OUTPUT_FILE)

