
import json
from pathlib import Path
from normalize import normalize_text

INPUT_DIR = Path("data/staged")
OUTPUT_DIR = Path("data/normalized")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

FILES = [
    "comi_hindi.jsonl",
    "hinge_hinglish.jsonl"
]

for filename in FILES:

    input_path = INPUT_DIR / filename
    output_path = OUTPUT_DIR / filename.replace(
        ".jsonl", "_normalized.jsonl"
    )

    processed = 0
    skipped = 0

    print("\nProcessing:", filename)

    with open(input_path, "r", encoding="utf-8") as source, \
         open(output_path, "w", encoding="utf-8") as output:

        for line in source:

            try:
                record = json.loads(line)

                if not isinstance(record, dict):
                    skipped += 1
                    continue

                if not isinstance(record.get("text"), str):
                    skipped += 1
                    continue

                record["text"] = normalize_text(record["text"])

                # Preserve even empty text for later quality filtering
                output.write(
                    json.dumps(record, ensure_ascii=False) + "\n"
                )

                processed += 1

            except (json.JSONDecodeError, TypeError):
                skipped += 1

    print("Processed:", processed)
    print("Skipped:", skipped)
    print("Output:", output_path)

print("\nBatch normalization completed!")
