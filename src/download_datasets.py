
from huggingface_hub import hf_hub_download
from pathlib import Path
import shutil
import hashlib
import json
from datetime import datetime, timezone

# Project folders
RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

# Dataset details
sources = [
    {
        "name": "COMI-LINGUA",
        "repo": "LingoIITGN/COMI-LINGUA",
        "file": "LID_train.csv",
        "url": "https://huggingface.co/datasets/LingoIITGN/COMI-LINGUA",
        "license": "CC BY 4.0"
    },
    {
        "name": "HinGE",
        "repo": "LingoIITGN/HinGE",
        "file": "HinGE.csv",
        "url": "https://huggingface.co/datasets/LingoIITGN/HinGE",
        "license": "CC BY 4.0"
    }
]

manifest = []

def calculate_hash(path):
    sha = hashlib.sha256()

    with open(path, "rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            sha.update(chunk)

    return sha.hexdigest()


for source in sources:
    print("\nDownloading:", source["name"])

    try:
        downloaded_path = hf_hub_download(
            repo_id=source["repo"],
            filename=source["file"],
            repo_type="dataset"
        )

        destination = RAW_DIR / source["file"]

        # Preserve original downloaded file
        shutil.copy2(downloaded_path, destination)

        file_hash = calculate_hash(destination)

        manifest.append({
            "name": source["name"],
            "url": source["url"],
            "license": source["license"],
            "filename": source["file"],
            "download_date_utc": datetime.now(
                timezone.utc
            ).isoformat(),
            "sha256": file_hash,
            "size_bytes": destination.stat().st_size
        })

        print("Saved:", destination)
        print("Size:", destination.stat().st_size, "bytes")
        print("SHA256:", file_hash)

    except Exception as error:
        print("Download failed:", source["name"])
        print("Reason:", error)
        raise

# Save source information
manifest_path = RAW_DIR / "sources_manifest.json"

with open(manifest_path, "w", encoding="utf-8") as file:
    json.dump(manifest, file, ensure_ascii=False, indent=4)

print("\nAll downloads completed!")
print("Source manifest:", manifest_path)
