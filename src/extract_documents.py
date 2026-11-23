
import csv
import ast
import json
from pathlib import Path

RAW_DIR = Path("data/raw")
STAGED_DIR = Path("data/staged")

STAGED_DIR.mkdir(parents=True, exist_ok=True)


def write_jsonl(file, record):
    file.write(
        json.dumps(record, ensure_ascii=False) + "\n"
    )


# --------------------------------
# 1. Extract Hindi Devanagari text
# --------------------------------

comi_input = RAW_DIR / "LID_train.csv"
comi_output = STAGED_DIR / "comi_hindi.jsonl"

comi_count = 0
comi_skipped = 0

with open(comi_input, encoding="utf-8-sig", newline="") as source:
    reader = csv.DictReader(source)

    with open(comi_output, "w", encoding="utf-8") as output:
        for row_number, row in enumerate(reader, start=1):
            try:
                text = (row.get("Sentences") or "").strip()

                if not text:
                    comi_skipped += 1
                    continue

                record = {
                    "id": f"COMI_{row_number:06d}",
                    "text": text,
                    "source": "COMI-LINGUA",
                    "source_row": row_number
                }

                write_jsonl(output, record)
                comi_count += 1

            except Exception:
                comi_skipped += 1


# --------------------------------
# 2. Extract Hinglish alternatives
# --------------------------------

hinge_input = RAW_DIR / "HinGE.csv"
hinge_output = STAGED_DIR / "hinge_hinglish.jsonl"

hinge_count = 0
hinge_skipped = 0

with open(hinge_input, encoding="utf-8-sig", newline="") as source:
    reader = csv.DictReader(source)

    with open(hinge_output, "w", encoding="utf-8") as output:
        for row_number, row in enumerate(reader, start=1):
            try:
                value = row.get("Human-generated Hinglish")

                if not value:
                    hinge_skipped += 1
                    continue

                alternatives = ast.literal_eval(value)

                if not isinstance(alternatives, list):
                    hinge_skipped += 1
                    continue

                for index, sentence in enumerate(alternatives, start=1):

                    if not isinstance(sentence, str):
                        hinge_skipped += 1
                        continue

                    text = sentence.strip()

                    if not text:
                        hinge_skipped += 1
                        continue

                    record = {
                        "id": f"HINGE_{row_number:06d}_{index:02d}",
                        "text": text,
                        "source": "HinGE",
                        "source_row": row_number,
                        "variant": index
                    }

                    write_jsonl(output, record)
                    hinge_count += 1

            except (ValueError, SyntaxError, TypeError):
                hinge_skipped += 1


# --------------------------------
# 3. Print extraction statistics
# --------------------------------

print("\n========== EXTRACTION REPORT ==========")

print("\nCOMI-LINGUA")
print("Extracted documents:", comi_count)
print("Skipped rows:", comi_skipped)
print("Output:", comi_output)

print("\nHinGE")
print("Extracted alternatives:", hinge_count)
print("Skipped rows:", hinge_skipped)
print("Output:", hinge_output)

print("\nTOTAL EXTRACTED:", comi_count + hinge_count)

print("\nExtraction completed!")
