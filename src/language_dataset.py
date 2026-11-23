
import json
from pathlib import Path
from collections import Counter

from language import identify_language


INPUT_DIR = Path("data/normalized")
OUTPUT_DIR = Path("data/labeled")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

FILES = [
    "comi_hindi_normalized.jsonl",
    "hinge_hinglish_normalized.jsonl"
]

total_counts = Counter()


for filename in FILES:

    input_path = INPUT_DIR / filename
    output_path = OUTPUT_DIR / filename.replace(
        "_normalized.jsonl", "_labeled.jsonl"
    )

    counts = Counter()
    skipped = 0
    samples = []

    print("\nProcessing:", filename)

    with open(input_path, "r", encoding="utf-8") as source, \
         open(output_path, "w", encoding="utf-8") as output:

        for line in source:

            try:
                record = json.loads(line)

                if not isinstance(record, dict):
                    skipped += 1
                    continue

                text = record.get("text")

                if not isinstance(text, str):
                    skipped += 1
                    continue

                lang = identify_language(text)

                record["lang"] = lang

                output.write(
                    json.dumps(record, ensure_ascii=False) + "\n"
                )

                counts[lang] += 1

                if len(samples) < 3:
                    samples.append({
                        "text": text[:100],
                        "lang": lang
                    })

            except (json.JSONDecodeError, TypeError):
                skipped += 1

    print("Language counts:")

    for language in ["hi", "hi-Latn", "en", "other"]:
        print(f"{language}: {counts[language]}")

    print("Skipped:", skipped)
    print("Output:", output_path)

    print("\nSample classifications:")

    for sample in samples:
        print(sample)

    total_counts.update(counts)


print("\n========== FINAL LANGUAGE REPORT ==========")

for language in ["hi", "hi-Latn", "en", "other"]:
    print(f"{language}: {total_counts[language]}")

print("TOTAL:", sum(total_counts.values()))

print("\nLanguage identification completed!")
