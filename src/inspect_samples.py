
import json
import random
from pathlib import Path

random.seed(42)

FILES = [
    "data/labeled/comi_hindi_labeled.jsonl",
    "data/labeled/hinge_hinglish_labeled.jsonl"
]

for filename in FILES:

    print("\n" + "=" * 60)
    print("FILE:", filename)
    print("=" * 60)

    samples = []

    with open(filename, encoding="utf-8") as file:
        for line in file:
            record = json.loads(line)
            samples.append(record)

    selected = random.sample(
        samples,
        min(10, len(samples))
    )

    for index, record in enumerate(selected, 1):

        print(f"\nSample {index}")
        print("ID:", record.get("id"))
        print("Language:", record.get("lang"))
        print("Text:", record.get("text"))

print("\nSample inspection completed!")
