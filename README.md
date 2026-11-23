# Hindi and Hinglish Data Processing Pipeline

## Overview
A pipeline for cleaning Hindi, Hinglish, and English text datasets.

## Data Sources
- COMI-LINGUA: https://huggingface.co/datasets/LingoIITGN/COMI-LINGUA
- HinGE: https://huggingface.co/datasets/LingoIITGN/HinGE

## Requirements
- Python 3.10+
- Dependencies in requirements.txt
- Git Bash for shell scripts

## Installation
```bash
pip install -r requirements.txt
```

## Download Data
```bash
./download.sh
```

## Run Pipeline
```bash
./run.sh data/raw output
```

## Outputs
- clean/training.jsonl.gz
- clean/sample_1000.jsonl
- eval.jsonl
- ledger.jsonl
- contamination.jsonl
- manifest.json

## Limitations
Language identification and PII detection are heuristic. Near-duplicate candidates require human review. See DECISIONS.md for details.
