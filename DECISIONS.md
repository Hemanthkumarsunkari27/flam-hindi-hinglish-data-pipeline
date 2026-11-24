
# Flam Indic Training Corpus — Decisions

## 1. Sources
- **COMI-LINGUA** — CC BY 4.0; 30,487 CSV rows; 123,492,954 bytes. [Dataset](https://huggingface.co/datasets/LingoIITGN/COMI-LINGUA)
- **HinGE** — CC BY 4.0; 1,976 CSV rows; 1,591,630 bytes. Extraction produced 4,799 Hinglish alternatives. [Dataset](https://huggingface.co/datasets/LingoIITGN/HinGE)
- Raw files and SHA-256 hashes are recorded in `data/raw/sources_manifest.json`.

## 2. Processing funnel
- Extracted: 35,286 documents (30,487 COMI-LINGUA and 4,799 HinGE alternatives).
- Language labeled: 35,286 — hi: 22,193; hi-Latn: 9,056; en: 4,037.
- Quality filtered: 34,822 — hi: 22,193; hi-Latn: 8,695; en: 3,934. Dropped: 464.
- PII redacted: 34,822. Six documents contained PII; seven total replacements were made.
- Exact deduplication: 34,809. Removed 13 exact duplicates.
- Evaluation holdout: 200 documents (127 hi, 50 hi-Latn, 23 en).
- Confirmed evaluation near-copy leaks removed: 4.
- Final training: 34,605 — hi: 22,056; hi-Latn: 8,639; en: 3,910.

Language labels use a rule-based heuristic, not source labels. The labels have not been independently human-validated.

## 3. Near-duplicate decisions
- Method: character-level TF-IDF with character n-grams of 3–5; cosine similarity.
- Threshold: 0.90, selected after inspecting candidate pairs from this corpus.
- 253 candidate pairs were generated; the first 40 high-scoring pairs were manually reviewed.
- Examples and decisions:
  - COMI_001474 / COMI_005429: “निफ्टी” versus “निफ्टी50”; preserved because the added number may change meaning.
  - COMI_026114 / COMI_026115: one version adds “अमेरिकी”; preserved because it adds a factual detail.
  - HINGE_001280_01 / HINGE_001280_02: reordered words; preserved pending review.
- Similarity alone was not used to delete corpus documents.

## 4. Quality filters
- Checks include empty text, encoding-corruption markers, control characters, markup and excessive character repetition.
- 459 records were rejected for possible encoding corruption and 5 for excessive character repetition.
- The five repeated-character examples included expressive social-media spellings. These are potential false positives; the filter trades some expressive text recall for quality.
- Repeated-word filtering was avoided because it rejected legitimate Hinglish examples.

## 5. PII and contamination
- PII patterns cover Indian phone numbers, email, Aadhaar and PAN, replaced with `<PHONE>`, `<EMAIL>`, `<AADHAAR>` and `<PAN>`.
- Six documents contained PII; seven replacements were made. Pattern-based detection may miss unusual formats.
- Exact and normalized-exact evaluation leakage: 0 matches.
- Near-copy comparison at 0.90: 6 candidates; 4 confirmed formatting-only copies were removed from training. Two candidates were preserved because they differed in city/date or added content.
- Cross-script comparison used Devanagari-to-IAST transliteration and character TF-IDF at 0.70. No candidates were found.
- The evaluation set measures held-out language and text-quality behaviour. Its heuristic language labels are not gold labels.

## 6. Reproducibility
- Raw source files, source metadata, download dates and SHA-256 hashes are retained.
- Evaluation sampling uses random seed 42.
- Processing thresholds and output counts are recorded in `output/manifest.json`.
- `download.sh` handles data acquisition separately from processing. `run.sh` invokes the Python pipeline runner. The runner was successfully tested on the supplied raw datasets. It uses a temporary workspace and refuses to overwrite an existing output directory. The shell wrapper itself and unseen follow-up data still require testing.

## 7. Scaling to 2 TB
The current in-memory TF-IDF comparison and pairwise similarity computation would become a bottleneck in memory and compute. At 2 TB, I would use partitioned object-storage reads, streaming preprocessing, distributed deduplication, and persistent fingerprints or MinHash/LSH candidate generation. Intermediate outputs would be checkpointed by partition so failed jobs can resume without duplicating records.

## 8. Not completed / priorities
1. Test the shell wrapper in a Bash-compatible environment and validate unseen follow-up input.
2. Improve and manually validate language identification and PII detection.
3. Expand near-duplicate and cross-script evaluation.
4. Review potential quality-filter false positives.
5. Improve scalability and checkpointing for large datasets.

Actual time spent: approximately 4 hours 20 minutes.


## 9. Final Testing and Limitations

- **Pipeline test:** Successfully ran all 17 stages using Git Bash with the project virtual environment activated.
- **Restart test:** Interrupted the pipeline during Stage 4 and reran it from the beginning. The final uncompressed training data matched the original output's SHA-256 hash.
- **Unseen content test:** Tested extraction with 3 new Hindi records and 2 new Hinglish records using the same CSV structure. All 5 records were extracted successfully, with 0 skipped rows.
- **Format limitation:** The current extractor supports the two source CSV formats and their expected column names. Other formats require an extraction adapter.
- **Restart limitation:** The pipeline safely restarts from the beginning after interruption; it does not resume from the last completed stage.
- **Scalability limitation:** Near-duplicate detection and evaluation splitting currently use in-memory processing. These stages need improvement for very large datasets.