
import json
from collections import Counter
from pathlib import Path

files = {
    "Staged": [
        Path("data/staged/comi_hindi.jsonl"),
        Path("data/staged/hinge_hinglish.jsonl"),
    ],
    "Normalized": [
        Path("data/normalized/comi_hindi_normalized.jsonl"),
        Path("data/normalized/hinge_hinglish_normalized.jsonl"),
    ],
    "Language labeled": [
        Path("data/labeled/comi_hindi_labeled.jsonl"),
        Path("data/labeled/hinge_hinglish_labeled.jsonl"),
    ],
    "Quality filtered": [
        Path("data/quality_filtered/quality_filtered.jsonl"),
    ],
    "PII redacted": [
        Path("data/pii_redacted/pii_redacted.jsonl"),
    ],
    "Exact deduplicated": [
        Path("data/exact_deduplicated/exact_deduplicated.jsonl"),
    ],
    "Final training": [
        Path("data/eval/training_pool_leak_free.jsonl"),
    ],
}

for stage, paths in files.items():
    counts = Counter()
    total = 0

    for path in paths:
        with path.open("r", encoding="utf-8") as file:
            for line in file:
                try:
                    record = json.loads(line)
                    counts[record.get("lang", "not_labeled")] += 1
                    total += 1
                except json.JSONDecodeError:
                    continue

    print("\n" + stage)
    print("Total:", total)
    print("Languages:", dict(counts))
