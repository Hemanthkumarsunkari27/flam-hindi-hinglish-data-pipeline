
import json
from pathlib import Path

from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate
from sklearn.feature_extraction.text import TfidfVectorizer

EVAL_FILE = Path("data/eval/eval.jsonl")
TRAIN_FILE = Path("data/eval/training_pool_leak_free.jsonl")
OUTPUT_FILE = Path("data/eval/cross_script_candidates.jsonl")

eval_records = [
    json.loads(line)
    for line in EVAL_FILE.open(encoding="utf-8")
]

train_records = [
    json.loads(line)
    for line in TRAIN_FILE.open(encoding="utf-8")
]


def has_devanagari(text):
    return any("\u0900" <= char <= "\u097f" for char in text)


def to_roman(text):
    return transliterate(text, sanscript.DEVANAGARI, sanscript.IAST)


# Keep only documents with the relevant scripts.
eval_hindi = [r for r in eval_records if r["lang"] == "hi" and has_devanagari(r["text"])]
train_hinglish = [r for r in train_records if r["lang"] == "hi-Latn"]

print("Evaluation Hindi documents:", len(eval_hindi))
print("Training Hinglish documents:", len(train_hinglish))

if not eval_hindi or not train_hinglish:
    raise ValueError("Not enough documents for cross-script comparison.")

eval_texts = [to_roman(r["text"]) for r in eval_hindi]
train_texts = [r["text"] for r in train_hinglish]

vectorizer = TfidfVectorizer(
    analyzer="char",
    ngram_range=(3, 5),
    min_df=2,
    max_df=0.5,
    max_features=200000,
    sublinear_tf=True,
    dtype="float32"
)

combined = vectorizer.fit_transform(train_texts + eval_texts)

train_matrix = combined[:len(train_texts)]
eval_matrix = combined[len(train_texts):]

similarities = eval_matrix @ train_matrix.T

matches = []

for i in range(similarities.shape[0]):
    row = similarities.getrow(i)

    for j, score in zip(row.indices, row.data):
        if score >= 0.70:
            matches.append({
                "eval_id": eval_hindi[i]["id"],
                "train_id": train_hinglish[j]["id"],
                "similarity": round(float(score), 4),
                "match_type": "cross_script_candidate"
            })

with OUTPUT_FILE.open("w", encoding="utf-8") as file:
    for match in matches:
        file.write(json.dumps(match, ensure_ascii=False) + "\n")

print("Cross-script check completed!")
print("Candidates found:", len(matches))
print("Report:", OUTPUT_FILE)
