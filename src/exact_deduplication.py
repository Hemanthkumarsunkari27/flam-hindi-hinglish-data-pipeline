
import json
import hashlib
import re
import unicodedata
from pathlib import Path

INPUT_FILE = Path("data/pii_redacted/pii_redacted.jsonl")

OUTPUT_DIR = Path("data/exact_deduplicated")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "exact_deduplicated.jsonl"
LEDGER_FILE = OUTPUT_DIR / "exact_deduplication_ledger.jsonl"


def normalize_for_comparison(text):
    """Normalize text only for duplicate comparison."""
    text = unicodedata.normalize("NFC", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def write_jsonl(file, record):
    file.write(json.dumps(record, ensure_ascii=False) + "\n")


def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Input not found: {INPUT_FILE}")

    seen_hashes = {}

    total = 0
    kept = 0
    duplicates = 0
    malformed = 0

    with open(INPUT_FILE, "r", encoding="utf-8") as source, \
         open(OUTPUT_FILE, "w", encoding="utf-8") as output, \
         open(LEDGER_FILE, "w", encoding="utf-8") as ledger:

        for line_number, line in enumerate(source, start=1):
            try:
                record = json.loads(line)

                if not isinstance(record, dict):
                    raise ValueError("Record is not a JSON object")

                text = record.get("text")

                if not isinstance(text, str) or not text.strip():
                    raise ValueError("Missing or empty text")

                total += 1

                comparison_text = normalize_for_comparison(text)

                digest = hashlib.sha256(
                    comparison_text.encode("utf-8")
                ).hexdigest()

                document_id = record.get(
                    "id", f"MISSING_ID_{line_number}"
                )

                if digest in seen_hashes:
                    duplicates += 1

                    write_jsonl(ledger, {
                        "id": document_id,
                        "status": "duplicate",
                        "stage": "exact_deduplication",
                        "reason": "exact_duplicate",
                        "dup_of": seen_hashes[digest]
                    })

                else:
                    seen_hashes[digest] = document_id

                    write_jsonl(output, record)
                    kept += 1

                    write_jsonl(ledger, {
                        "id": document_id,
                        "status": "kept",
                        "stage": "exact_deduplication",
                        "reason": "unique_text",
                        "dup_of": None
                    })

            except (json.JSONDecodeError, ValueError, TypeError):
                malformed += 1

                write_jsonl(ledger, {
                    "id": f"MALFORMED_{line_number}",
                    "status": "skipped",
                    "stage": "exact_deduplication",
                    "reason": "malformed_json_record",
                    "dup_of": None
                })

    print("\n========== EXACT DEDUPLICATION REPORT ==========")
    print("Documents processed:", total)
    print("Unique documents kept:", kept)
    print("Exact duplicates removed:", duplicates)
    print("Malformed records:", malformed)
    print("Total input lines:", total + malformed)

    print("\nClean output:", OUTPUT_FILE)
    print("Ledger:", LEDGER_FILE)
    print("\nExact deduplication completed!")


if __name__ == "__main__":
    main()
