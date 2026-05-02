"""
Utilities for uploading evaluation artifacts to AWS S3.
"""

from __future__ import annotations

import csv
import io
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

try:
    import boto3
except ImportError:  # pragma: no cover - handled at runtime
    boto3 = None


@dataclass
class S3ArtifactUploader:
    """Upload local files or directories to S3."""

    bucket: str
    prefix: str = "artifacts/"
    region_name: Optional[str] = None
    use_iam_role: bool = False

    def _client(self):
        if boto3 is None:
            raise RuntimeError(
                "boto3 is not installed. Install backend requirements to enable S3 uploads."
            )

        session_kwargs = {}
        if self.region_name:
            session_kwargs["region_name"] = self.region_name

        session = boto3.Session(**session_kwargs)
        client_kwargs = {}
        if self.use_iam_role:
            client_kwargs["aws_access_key_id"] = None
            client_kwargs["aws_secret_access_key"] = None
            client_kwargs["aws_session_token"] = None

        return session.client("s3", **client_kwargs)

    @staticmethod
    def _normalize_prefix(prefix: str) -> str:
        normalized = (prefix or "").strip().lstrip("/")
        if normalized and not normalized.endswith("/"):
            normalized += "/"
        return normalized

    def upload_file(self, local_path: str | Path, s3_key: Optional[str] = None) -> str:
        path = Path(local_path)
        if not path.exists():
            raise FileNotFoundError(f"Local file not found: {path}")

        key = s3_key or path.name
        key = f"{self._normalize_prefix(self.prefix)}{key}".replace("//", "/")

        client = self._client()
        client.upload_file(str(path), self.bucket, key)
        return f"s3://{self.bucket}/{key}"

    def upload_many(self, files: Iterable[str | Path], subdir: Optional[str] = None) -> list[str]:
        uploaded = []
        relative_prefix = ""
        if subdir:
            relative_prefix = f"{subdir.strip('/')}/"

        for file_path in files:
            path = Path(file_path)
            uploaded.append(self.upload_file(path, f"{relative_prefix}{path.name}".replace("//", "/")))
        return uploaded

    def upload_directory(self, directory: str | Path, pattern: str = "*.png", subdir: Optional[str] = None) -> list[str]:
        root = Path(directory)
        if not root.exists():
            raise FileNotFoundError(f"Directory not found: {root}")

        files = sorted(root.rglob(pattern))
        if not files:
            return []

        uploaded = []
        for path in files:
            relative = path.relative_to(root).as_posix()
            key_parts = []
            if subdir:
                key_parts.append(subdir.strip('/').replace('\\', '/'))
                key_parts.append('/')
            key_parts.append(relative)
            s3_key = ''.join(key_parts).replace('//', '/')
            uploaded.append(self.upload_file(path, s3_key))
        return uploaded

    def append_csv_row(self, s3_key: str, row: dict, fieldnames: list[str]) -> str:
        """Append a single row to a CSV object stored in S3.

        If the object does not exist yet, it creates it with a header row.
        """
        client = self._client()
        key = f"{self._normalize_prefix(self.prefix)}{s3_key.lstrip('/')}".replace("//", "/")

        rows = []
        try:
            response = client.get_object(Bucket=self.bucket, Key=key)
            existing_body = response["Body"].read().decode("utf-8")
            if existing_body.strip():
                reader = csv.DictReader(io.StringIO(existing_body))
                rows.extend(reader)
        except Exception:
            # If the object does not exist yet, start a new CSV.
            pass

        rows.append({name: row.get(name, "") for name in fieldnames})

        buffer = io.StringIO()
        writer = csv.DictWriter(buffer, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

        client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=buffer.getvalue().encode("utf-8"),
            ContentType="text/csv",
        )
        return f"s3://{self.bucket}/{key}"


def build_artifact_uploader():
    """Build an uploader from environment variables."""
    bucket = os.getenv("AWS_S3_BUCKET", "").strip()
    if not bucket:
        raise ValueError("AWS_S3_BUCKET is required for S3 artifact uploads")

    return S3ArtifactUploader(
        bucket=bucket,
        prefix=os.getenv("AWS_S3_ARTIFACTS_PREFIX", "artifacts/"),
        region_name=os.getenv("AWS_REGION", "us-east-1"),
        use_iam_role=os.getenv("USE_IAM_ROLE", "False").lower() == "true",
    )
