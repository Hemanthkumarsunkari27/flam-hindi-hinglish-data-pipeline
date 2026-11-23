
import gzip
import json
from pathlib import Path

INPUT_FILE = Path("data/eval/training_pool_leak_free.jsonl")
OUTPUT_DIR = Path("output/clean")
OUTPUT_FILE = OUTPUT_DIR / "training.jsonl.gz"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

count = 0

with INPUT_FILE.open("r", encoding="utf-8") as source:
    with gzip.open(OUTPUT_FILE, "wt", encoding="utf-8") as output:
        for line in source:
            try:
                record = json.loads(line)
                output.write(json.dumps(record, ensure_ascii=False) + "\n")
                count += 1
            except json.JSONDecodeError:
                continue

print("Final dataset created!")
print("Documents:", count)
print("Output:", OUTPUT_FILE)
print("Compressed size (MB):", round(OUTPUT_FILE.stat().st_size / (1024 * 1024), 2))
