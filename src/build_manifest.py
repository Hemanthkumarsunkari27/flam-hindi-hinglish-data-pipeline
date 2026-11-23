
import json
import gzip
import hashlib
from collections import Counter
from pathlib import Path

ROOT = Path(".")
OUTPUT = ROOT / "output" / "manifest.json"


def load_json(path):
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def count_jsonl(path, compressed=False):
    count = 0
    languages = Counter()

    opener = gzip.open if compressed else open

    with opener(path, "rt", encoding="utf-8") as file:
        for line in file:
            try:
                record = json.loads(line)
                count += 1
                if "lang" in record:
                    languages[record["lang"]] += 1
            except json.JSONDecodeError:
                continue

    return count, dict(languages)


def sha256_file(path):
    digest = hashlib.sha256()

    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


source_manifest = load_json(ROOT / "data/raw/sources_manifest.json")

training_file = ROOT / "output/clean/training.jsonl.gz"
evaluation_file = ROOT / "output/eval.jsonl"
ledger_file = ROOT / "output/ledger.jsonl"
contamination_file = ROOT / "output/contamination.jsonl"
training_pool = ROOT / "data/eval/training_pool_leak_free.jsonl"

training_count, language_counts = count_jsonl(training_file, compressed=True)
evaluation_count, _ = count_jsonl(evaluation_file)
ledger_count, _ = count_jsonl(ledger_file)
contamination_count, _ = count_jsonl(contamination_file)

status_counts = Counter()
stage_counts = Counter()

with ledger_file.open("r", encoding="utf-8") as file:
    for line in file:
        record = json.loads(line)
        status_counts[record["status"]] += 1
        stage_counts[record["stage"]] += 1

raw_sources = []

for source in source_manifest:
    raw_path = ROOT / "data" / "raw" / source["filename"]
    raw_sources.append({
        "name": source["name"],
        "filename": source["filename"],
        "size_bytes": raw_path.stat().st_size,
        "sha256": sha256_file(raw_path),
        "download_date_utc": source["download_date_utc"],
        "license": source["license"],
        "url": source["url"]
    })

manifest = {
    "project": "Flam Indic Training Corpus",
    "created_date": "2026-11-23",
    "sources": raw_sources,
    "processing": {
        "normalization": "Unicode NFC, invisible character cleanup and whitespace normalization",
        "language_labels": ["hi", "hi-Latn", "en", "other"],
        "language_identification": "Rule-based heuristic; labels are not manually validated",
        "quality_filtering": "Encoding, markup, control-character and excessive-character checks",
        "pii_redaction": ["PHONE", "EMAIL", "AADHAAR", "PAN"],
        "exact_deduplication": "Exact text matching after PII redaction",
        "near_duplicate_method": "Character TF-IDF, 3-5 character n-grams",
        "near_duplicate_threshold": 0.90,
        "evaluation_random_seed": 42,
        "evaluation_size": evaluation_count,
        "confirmed_near_copy_leaks_removed": 4,
        "cross_script_method": "Indic transliteration and character TF-IDF",
        "cross_script_threshold": 0.70,
        "cross_script_candidates": 0
    },
    "final_counts": {
        "training_documents": training_count,
        "evaluation_documents": evaluation_count,
        "ledger_documents": ledger_count,
        "contamination_records": contamination_count,
        "ledger_statuses": dict(status_counts),
        "ledger_stages": dict(stage_counts),
        "training_language_distribution": language_counts
    },
    "outputs": {
        "training_dataset": {
            "path": "output/clean/training.jsonl.gz",
            "size_bytes": training_file.stat().st_size,
            "sha256": sha256_file(training_file)
        },
        "evaluation_set": {
            "path": "output/eval.jsonl",
            "size_bytes": evaluation_file.stat().st_size,
            "sha256": sha256_file(evaluation_file)
        },
        "consolidated_ledger": {
            "path": "output/ledger.jsonl",
            "size_bytes": ledger_file.stat().st_size,
            "sha256": sha256_file(ledger_file)
        },
        "contamination_report": {
            "path": "output/contamination.jsonl",
            "records": contamination_count
        }
    }
}

OUTPUT.parent.mkdir(parents=True, exist_ok=True)

with OUTPUT.open("w", encoding="utf-8") as file:
    json.dump(manifest, file, ensure_ascii=False, indent=4)

print("Manifest created successfully!")
print("Training documents:", training_count)
print("Evaluation documents:", evaluation_count)
print("Ledger documents:", ledger_count)
print("Ledger statuses:", dict(status_counts))
print("Contamination records:", contamination_count)
print("Manifest:", OUTPUT)

