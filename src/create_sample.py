
import gzip
import json
import random
from pathlib import Path

INPUT_FILE = Path("output/clean/training.jsonl.gz")
OUTPUT_FILE = Path("output/clean/sample_1000.jsonl")

SEED = 42
SAMPLE_SIZE = 1000

records = []

with gzip.open(INPUT_FILE, "rt", encoding="utf-8") as file:
    for line in file:
        records.append(json.loads(line))

if len(records) < SAMPLE_SIZE:
    raise ValueError("Training dataset contains fewer than 1000 records.")

rng = random.Random(SEED)
sample = rng.sample(records, SAMPLE_SIZE)

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

with OUTPUT_FILE.open("w", encoding="utf-8") as file:
    for record in sample:
        file.write(json.dumps(record, ensure_ascii=False) + "\n")

print("Sample created successfully!")
print("Sample records:", len(sample))
print("Random seed:", SEED)
print("Output:", OUTPUT_FILE)
