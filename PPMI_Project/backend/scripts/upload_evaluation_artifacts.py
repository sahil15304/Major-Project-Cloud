"""
Upload evaluation and interpretability plots to AWS S3.

Usage:
  python scripts/upload_evaluation_artifacts.py

Environment:
  AWS_S3_BUCKET              Required
  AWS_S3_ARTIFACTS_PREFIX    Optional, defaults to artifacts/
  AWS_REGION                 Optional, defaults to us-east-1
  USE_IAM_ROLE               Optional, defaults to False
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.utils.s3_storage import build_artifact_uploader  # noqa: E402


def upload_graphs() -> None:
    uploader = build_artifact_uploader()

    folders = [
        (ROOT / "eval", "eval"),
        (ROOT / "interpretability", "interpretability"),
    ]

    uploaded = []
    for folder, subdir in folders:
        if folder.exists():
            uploaded.extend(uploader.upload_directory(folder, pattern="*.png", subdir=subdir))

    if uploaded:
        print("Uploaded artifacts:")
        for item in uploaded:
            print(f"- {item}")
    else:
        print("No PNG artifacts found to upload.")


if __name__ == "__main__":
    upload_graphs()