
import json
import re
from pathlib import Path

INPUT_FILES = [
    Path("data/labeled/comi_hindi_labeled.jsonl"),
    Path("data/labeled/hinge_hinglish_labeled.jsonl"),
]

OUTPUT_DIR = Path("data/quality_filtered")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "quality_filtered.jsonl"
LEDGER_FILE = OUTPUT_DIR / "quality_filter_ledger.jsonl"


# Recognize common HTML/XML markup rather than treating
# ordinary angle-bracket text as markup.
MARKUP_PATTERN = re.compile(
    r"<\s*/?\s*(html|body|div|span|p|br|script|style|table|tr|td|"
    r"head|iframe|meta|link|!doctype)\b[^>]*>",
    re.IGNORECASE,
)

# Obvious signs of broken text encoding.
MOJIBAKE_MARKERS = [
    "\ufffd",       # Unicode replacement character
    "\x00",         # Null byte
    "Ã", "Â", "â€",
]

def check_quality(text):
    if not isinstance(text, str) or not text.strip():
        return False, "empty_text"

    text = text.strip()

    # Detect likely encoding corruption
    if any(marker in text for marker in MOJIBAKE_MARKERS):
        return False, "possible_encoding_corruption"

    # Detect invalid control characters
    for char in text:
        if ord(char) < 32 and char not in "\n\r\t":
            return False, "control_characters"

    # Detect HTML/XML markup
    if MARKUP_PATTERN.search(text):
        return False, "html_or_xml_markup"

    # Detect unusually long repeated letters inside words.
    # Punctuation repetition and ordinary word repetition are allowed.
    if re.search(r"([A-Za-z])\1{11,}", text, re.IGNORECASE):
        return False, "excessive_character_repetition"

    return True, "passed_quality_checks"


def write_jsonl(file, record):
    file.write(
        json.dumps(record, ensure_ascii=False) + "\n"
    )


def main():

    kept_count = 0
    dropped_count = 0
    malformed_count = 0
    reason_counts = {}

    with open(OUTPUT_FILE, "w", encoding="utf-8") as output, \
         open(LEDGER_FILE, "w", encoding="utf-8") as ledger:

        for input_path in INPUT_FILES:

            print(f"\nProcessing: {input_path}")

            if not input_path.exists():
                raise FileNotFoundError(
                    f"Input file not found: {input_path}"
                )

            with open(input_path, "r", encoding="utf-8") as source:

                for line_number, line in enumerate(source, start=1):

                    try:
                        record = json.loads(line)

                        if not isinstance(record, dict):
                            raise ValueError("Record is not a JSON object")

                        document_id = record.get("id")

                        if not document_id:
                            document_id = (
                                f"MISSING_ID_{input_path.stem}_{line_number}"
                            )

                        text = record.get("text", "")
                        keep, reason = check_quality(text)

                        if keep:
                            write_jsonl(output, record)
                            kept_count += 1
                            status = "kept"
                        else:
                            dropped_count += 1
                            status = "dropped"

                        reason_counts[reason] = (
                            reason_counts.get(reason, 0) + 1
                        )

                        write_jsonl(ledger, {
                            "id": document_id,
                            "status": status,
                            "stage": "quality_filter",
                            "reason": reason,
                            "dup_of": None
                        })

                    except (json.JSONDecodeError, ValueError, TypeError):
                        malformed_count += 1
                        dropped_count += 1

                        document_id = (
                            f"MALFORMED_{input_path.stem}_{line_number}"
                        )

                        write_jsonl(ledger, {
                            "id": document_id,
                            "status": "dropped",
                            "stage": "quality_filter",
                            "reason": "malformed_json_record",
                            "dup_of": None
                        })

    print("\n========== QUALITY FILTER REPORT ==========")
    print("Kept:", kept_count)
    print("Dropped:", dropped_count)
    print("Malformed records:", malformed_count)
    print("Total processed:", kept_count + dropped_count)

    print("\nReason counts:")
    for reason, count in sorted(reason_counts.items()):
        print(f"{reason}: {count}")

    print("\nClean output:", OUTPUT_FILE)
    print("Ledger:", LEDGER_FILE)
    print("\nQuality filtering completed!")


if __name__ == "__main__":
    main()
