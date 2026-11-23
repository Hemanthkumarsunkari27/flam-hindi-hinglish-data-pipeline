#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 2 ]; then
    echo "Usage: ./run.sh <raw_dir> <out_dir>"
    exit 1
fi

python src/pipeline_runner.py "$1" "$2"
