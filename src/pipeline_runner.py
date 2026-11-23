
import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def run_pipeline(raw_dir, out_dir):
    project_root = Path(__file__).resolve().parent.parent

    raw_dir = Path(raw_dir).resolve()
    out_dir = Path(out_dir).resolve()

    required_files = [
        "LID_train.csv",
        "HinGE.csv",
        "sources_manifest.json",
    ]

    for filename in required_files:
        if not (raw_dir / filename).is_file():
            raise FileNotFoundError(
                f"Required file not found: {raw_dir / filename}"
            )

    if out_dir == raw_dir or raw_dir in out_dir.parents:
        raise ValueError(
            "Output directory must not be inside the raw-data directory."
        )

    if out_dir.exists():
        raise FileExistsError(
            f"Output directory already exists: {out_dir}\n"
            "Choose a new output directory to avoid deleting existing files."
        )

    print("\nStarting Flam Data Assignment pipeline...")
    print("Raw directory:", raw_dir)
    print("Output directory:", out_dir)

    stages = [
        "extract_documents.py",
        "normalize_dataset.py",
        "language_dataset.py",
        "quality_filter.py",
        "pii_redaction.py",
        "exact_deduplication.py",
        "near_duplicate_candidates.py",
        "create_eval_set.py",
        "check_contamination.py",
        "check_near_copy.py",
        "remove_eval_leaks.py",
        "check_cross_script.py",
        "build_final_dataset.py",
        "build_consolidated_ledger.py",
        "build_contamination_report.py",
        "create_sample.py",
        "build_manifest.py",
    ]

    with tempfile.TemporaryDirectory(prefix="flam_pipeline_") as temp:
        workspace = Path(temp)

        shutil.copytree(
            project_root / "src",
            workspace / "src"
        )

        shutil.copytree(
            raw_dir,
            workspace / "data" / "raw"
        )

        for index, stage in enumerate(stages, start=1):
            script = workspace / "src" / stage

            if not script.is_file():
                raise FileNotFoundError(
                    f"Pipeline script missing: {stage}"
                )

            # Copy the evaluation set before manifest generation.
            if stage == "build_manifest.py":
                eval_source = (
                    workspace / "data" / "eval" / "eval.jsonl"
                )
                eval_destination = (
                    workspace / "output" / "eval.jsonl"
                )

                if not eval_source.is_file():
                    raise FileNotFoundError(
                        "Evaluation file was not generated."
                    )

                eval_destination.parent.mkdir(
                    parents=True,
                    exist_ok=True
                )

                shutil.copy2(
                    eval_source,
                    eval_destination
                )

            print(f"\n[{index}/{len(stages)}] Running {stage}")

            subprocess.run(
                [sys.executable, str(script)],
                cwd=workspace,
                check=True
            )

        generated_output = workspace / "output"

        if not generated_output.is_dir():
            raise FileNotFoundError(
                "Pipeline did not create the output directory."
            )

        out_dir.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        shutil.copytree(
            generated_output,
            out_dir
        )

    print("\nPipeline completed successfully!")
    print("Final files saved to:", out_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run the Flam Data Assignment pipeline."
    )

    parser.add_argument(
        "raw_dir",
        help="Directory containing the raw CSV files"
    )

    parser.add_argument(
        "out_dir",
        help="Directory for final pipeline outputs"
    )

    args = parser.parse_args()

    try:
        run_pipeline(args.raw_dir, args.out_dir)
    except Exception as error:
        print("\nPIPELINE FAILED:", error)
        sys.exit(1)

