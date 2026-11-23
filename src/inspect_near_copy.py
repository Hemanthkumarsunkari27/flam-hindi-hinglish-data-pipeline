
import json
from pathlib import Path

eval_file = Path("data/eval/eval.jsonl")
train_file = Path("data/eval/training_pool.jsonl")
matches_file = Path("data/eval/near_copy_contamination.jsonl")

eval_records = {
    r["id"]: r
    for r in (json.loads(line) for line in eval_file.open(encoding="utf-8"))
}

train_records = {
    r["id"]: r
    for r in (json.loads(line) for line in train_file.open(encoding="utf-8"))
}

with matches_file.open("r", encoding="utf-8") as file:
    matches = [json.loads(line) for line in file]

for number, match in enumerate(matches, 1):
    evaluation = eval_records[match["eval_id"]]
    training = train_records[match["train_id"]]

    print("\n" + "=" * 70)
    print("PAIR:", number)
    print("Similarity:", match["similarity"])
    print("Evaluation ID:", evaluation["id"], "| Language:", evaluation["lang"])
    print("Training ID:", training["id"], "| Language:", training["lang"])
    print("EVALUATION TEXT:", evaluation["text"])
    print("TRAINING TEXT:", training["text"])

print("\nTotal candidate pairs:", len(matches))
