
import json
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

EVAL_FILE = Path("data/eval/eval.jsonl")
TRAIN_FILE = Path("data/eval/training_pool.jsonl")
OUTPUT_FILE = Path("data/eval/near_copy_contamination.jsonl")

THRESHOLD = 0.90


def load_records(path):
    records = []
    with path.open("r", encoding="utf-8") as file:
        for line in file:
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return records


evaluation = load_records(EVAL_FILE)
training = load_records(TRAIN_FILE)

# Exclude very short texts from similarity comparison.
eval_records = [r for r in evaluation if len(r["text"]) >= 20]
train_records = [r for r in training if len(r["text"]) >= 20]

eval_texts = [r["text"] for r in eval_records]
train_texts = [r["text"] for r in train_records]

print("Evaluation texts:", len(eval_texts))
print("Training texts:", len(train_texts))
print("Building character TF-IDF matrix...")

vectorizer = TfidfVectorizer(
    analyzer="char",
    ngram_range=(3, 5),
    min_df=2,
    max_df=0.5,
    max_features=200000,
    sublinear_tf=True,
    dtype=np.float32
)

combined = vectorizer.fit_transform(train_texts + eval_texts)

train_matrix = combined[:len(train_texts)]
eval_matrix = combined[len(train_texts):]

print("Comparing evaluation against training...")

similarities = eval_matrix @ train_matrix.T
matches = []

for i in range(similarities.shape[0]):
    row = similarities.getrow(i)

    for j, score in zip(row.indices, row.data):
        if score >= THRESHOLD:
            matches.append({
                "eval_id": eval_records[i]["id"],
                "train_id": train_records[j]["id"],
                "similarity": round(float(score), 4),
                "match_type": "near_copy_candidate"
            })

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

with OUTPUT_FILE.open("w", encoding="utf-8") as file:
    for match in matches:
        file.write(json.dumps(match, ensure_ascii=False) + "\n")

print("Near-copy check completed!")
print("Similarity threshold:", THRESHOLD)
print("Near-copy candidates:", len(matches))
print("Report:", OUTPUT_FILE)
