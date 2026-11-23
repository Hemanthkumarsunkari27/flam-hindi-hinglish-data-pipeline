
import json
import re
from pathlib import Path

INPUT_FILE = Path("data/quality_filtered/quality_filtered.jsonl")

OUTPUT_DIR = Path("data/pii_redacted")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "pii_redacted.jsonl"
LEDGER_FILE = OUTPUT_DIR / "pii_redaction_ledger.jsonl"

# Email addresses
EMAIL_PATTERN = re.compile(
    r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b"
)

# Indian Aadhaar: 12 digits, optionally separated into groups
AADHAAR_PATTERN = re.compile(
    r"(?<!\d)(?:\d{4}[\s-]?){2}\d{4}(?!\d)"
)

# Indian PAN: 5 letters, 4 digits, 1 letter
PAN_PATTERN = re.compile(
    r"(?i)(?<![A-Z0-9])[A-Z]{5}\d{4}[A-Z](?![A-Z0-9])"
)

# Indian mobile numbers, optionally with +91
PHONE_PATTERN = re.compile(
    r"(?<!\w)(?:\+91[\s-]?)?[6-9]\d{4}[\s-]?\d{5}(?!\w)"
)


def redact_pii(text):
    counts = {
        "PHONE": 0,
        "EMAIL": 0,
        "AADHAAR": 0,
        "PAN": 0
    }

    def replace_aadhaar(match):
        counts["AADHAAR"] += 1
        return "<AADHAAR>"

    def replace_pan(match):
        counts["PAN"] += 1
        return "<PAN>"

    def replace_email(match):
        counts["EMAIL"] += 1
        return "<EMAIL>"

    def replace_phone(match):
        counts["PHONE"] += 1
        return "<PHONE>"

    # Redact Aadhaar before phone numbers to avoid partial matches
    text = AADHAAR_PATTERN.sub(replace_aadhaar, text)
    text = PAN_PATTERN.sub(replace_pan, text)
    text = EMAIL_PATTERN.sub(replace_email, text)
    text = PHONE_PATTERN.sub(replace_phone, text)

    return text, counts


def write_jsonl(file, record):
    file.write(
        json.dumps(record, ensure_ascii=False) + "\n"
    )


def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Input file not found: {INPUT_FILE}"
        )

    total = 0
    malformed = 0
    documents_with_pii = 0

    total_counts = {
        "PHONE": 0,
        "EMAIL": 0,
        "AADHAAR": 0,
        "PAN": 0
    }

    with open(INPUT_FILE, "r", encoding="utf-8") as source, \
         open(OUTPUT_FILE, "w", encoding="utf-8") as output, \
         open(LEDGER_FILE, "w", encoding="utf-8") as ledger:

        for line_number, line in enumerate(source, start=1):
            try:
                record = json.loads(line)

                if not isinstance(record, dict):
                    raise ValueError("Record is not a JSON object")

                text = record.get("text", "")

                if not isinstance(text, str):
                    raise ValueError("Text field is not a string")

                redacted_text, counts = redact_pii(text)

                # Preserve all original record fields
                record["text"] = redacted_text

                write_jsonl(output, record)

                total += 1

                found = sum(counts.values())

                if found > 0:
                    documents_with_pii += 1

                for category, count in counts.items():
                    total_counts[category] += count

                write_jsonl(ledger, {
                    "id": record.get("id", f"MISSING_ID_{line_number}"),
                    "status": "processed",
                    "stage": "pii_redaction",
                    "reason": "pii_redacted" if found else "no_pii_found",
                    "redaction_counts": counts,
                    "dup_of": None
                })

            except (json.JSONDecodeError, ValueError, TypeError):
                malformed += 1

                write_jsonl(ledger, {
                    "id": f"MALFORMED_{line_number}",
                    "status": "skipped",
                    "stage": "pii_redaction",
                    "reason": "malformed_json_record",
                    "dup_of": None
                })

    print("\n========== PII REDACTION REPORT ==========")
    print("Documents processed:", total)
    print("Documents containing PII:", documents_with_pii)
    print("Malformed records:", malformed)

    print("\nTotal redactions:")
    for category, count in total_counts.items():
        print(f"{category}: {count}")

    print("\nTotal PII values redacted:", sum(total_counts.values()))
    print("\nClean output:", OUTPUT_FILE)
    print("Ledger:", LEDGER_FILE)
    print("\nPII redaction completed!")


if __name__ == "__main__":
    main()
