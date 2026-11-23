
import json
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

INPUT_FILE = Path("data/exact_deduplicated/exact_deduplicated.jsonl")
OUTPUT_FILE = Path("data/near_duplicate_candidates/candidates.jsonl")

CANDIDATE_THRESHOLD = 0.90
CHUNK_SIZE = 250
MIN_TEXT_LENGTH = 20


def load_documents():
    documents = []

    with INPUT_FILE.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            try:
                record = json.loads(line)
                text = record.get("text", "")

                if isinstance(text, str) and len(text.strip()) >= MIN_TEXT_LENGTH:
                    documents.append(record)

            except (json.JSONDecodeError, TypeError):
                print(f"Skipping malformed line: {line_number}")

    return documents


def main():
    print("Loading documents...")
    documents = load_documents()
    print(f"Documents loaded: {len(documents)}")

    texts = [doc["text"] for doc in documents]

    print("\nCreating character-level TF-IDF vectors...")

    vectorizer = TfidfVectorizer(
        analyzer="char",
        ngram_range=(3, 5),
        min_df=2,
        max_df=0.5,
        max_features=200000,
        sublinear_tf=True,
        dtype=np.float32
    )

    matrix = vectorizer.fit_transform(texts)
    print(f"TF-IDF matrix shape: {matrix.shape}")

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    candidate_count = 0

    print("\nFinding similar-text candidates...")

    with OUTPUT_FILE.open("w", encoding="utf-8") as output:
        for start in range(0, len(documents), CHUNK_SIZE):
            end = min(start + CHUNK_SIZE, len(documents))

            similarities = matrix[start:end] @ matrix.T

            for local_index in range(end - start):
                i = start + local_index
                row = similarities.getrow(local_index)

                valid = [
                    (int(j), float(score))
                    for j, score in zip(row.indices, row.data)
                    if j > i and score >= CANDIDATE_THRESHOLD
                ]

                valid.sort(key=lambda item: item[1], reverse=True)

                for j, score in valid:
                    pair = {
                        "id_1": documents[i]["id"],
                        "id_2": documents[j]["id"],
                        "language_1": documents[i].get("lang"),
                        "language_2": documents[j].get("lang"),
                        "similarity": round(score, 4),
                        "text_1": documents[i]["text"],
                        "text_2": documents[j]["text"]
                    }

                    output.write(json.dumps(pair, ensure_ascii=False) + "\n")
                    candidate_count += 1

            print(f"Processed {end}/{len(documents)} documents")

    print("\nNear-duplicate candidate generation complete.")
    print(f"Candidate pairs: {candidate_count}")
    print(f"Output: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
