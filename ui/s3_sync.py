"""
S3 Sync Layer for Smart Suite
Provides read/write to S3 for cross-environment data sharing (local ↔ Cloud).
Falls back to local filesystem if S3 is unavailable.
"""
import json
import os
from pathlib import Path
from datetime import datetime

# Config
S3_BUCKET = os.environ.get("SMARTSUITE_S3_BUCKET", "smartsuite-sync-data")
S3_PREFIX = "requests/"
AWS_REGION = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")

_s3_client = None


def _get_s3():
    """Lazy-init S3 client."""
    global _s3_client
    if _s3_client is None:
        try:
            import boto3

            # Try Streamlit secrets first (for Cloud deployment)
            try:
                import streamlit as st
                if hasattr(st, "secrets") and "aws" in st.secrets:
                    aws_secrets = st.secrets["aws"]
                    os.environ.setdefault("AWS_ACCESS_KEY_ID", aws_secrets.get("AWS_ACCESS_KEY_ID", ""))
                    os.environ.setdefault("AWS_SECRET_ACCESS_KEY", aws_secrets.get("AWS_SECRET_ACCESS_KEY", ""))
                    os.environ.setdefault("AWS_DEFAULT_REGION", aws_secrets.get("AWS_DEFAULT_REGION", AWS_REGION))
                    if "SMARTSUITE_S3_BUCKET" in aws_secrets:
                        global S3_BUCKET
                        S3_BUCKET = aws_secrets["SMARTSUITE_S3_BUCKET"]
            except Exception:
                pass

            _s3_client = boto3.client("s3", region_name=os.environ.get("AWS_DEFAULT_REGION", AWS_REGION))
            # Quick check: list bucket (will fail if no access)
            _s3_client.head_bucket(Bucket=S3_BUCKET)
        except Exception:
            _s3_client = False  # Mark as unavailable
    return _s3_client if _s3_client else None


def s3_available() -> bool:
    """Check if S3 is accessible."""
    return _get_s3() is not None


def save_user_data(user: str, filename: str, data: dict | list):
    """Save user data to S3 (and local fallback)."""
    content = json.dumps(data, ensure_ascii=False, indent=2)
    s3_key = f"{S3_PREFIX}{user}/{filename}"

    # Always try S3 first
    s3 = _get_s3()
    if s3:
        try:
            s3.put_object(Bucket=S3_BUCKET, Key=s3_key,
                          Body=content.encode("utf-8"),
                          ContentType="application/json")
            return True
        except Exception:
            pass
    return False


def load_user_data(user: str, filename: str, default=None):
    """Load user data from S3 (fallback to default)."""
    s3_key = f"{S3_PREFIX}{user}/{filename}"

    s3 = _get_s3()
    if s3:
        try:
            resp = s3.get_object(Bucket=S3_BUCKET, Key=s3_key)
            content = resp["Body"].read().decode("utf-8")
            return json.loads(content)
        except s3.exceptions.NoSuchKey:
            return default if default is not None else []
        except Exception:
            pass
    return default if default is not None else []


def save_shared_data(filename: str, data: dict | list):
    """Save shared data (not user-specific) to S3."""
    content = json.dumps(data, ensure_ascii=False, indent=2)
    s3_key = f"shared/{filename}"

    s3 = _get_s3()
    if s3:
        try:
            s3.put_object(Bucket=S3_BUCKET, Key=s3_key,
                          Body=content.encode("utf-8"),
                          ContentType="application/json")
            return True
        except Exception:
            pass
    return False


def load_shared_data(filename: str, default=None):
    """Load shared data from S3."""
    s3_key = f"shared/{filename}"

    s3 = _get_s3()
    if s3:
        try:
            resp = s3.get_object(Bucket=S3_BUCKET, Key=s3_key)
            content = resp["Body"].read().decode("utf-8")
            return json.loads(content)
        except Exception:
            pass
    return default if default is not None else []


def save_batch_file(batch_id: str, sub_path: str, content: str):
    """Save a batch file to S3. sub_path like '01_zhiku/zhiku_ai_queries.csv'"""
    s3_key = f"batches/{batch_id}/{sub_path}"
    s3 = _get_s3()
    if s3:
        try:
            s3.put_object(Bucket=S3_BUCKET, Key=s3_key,
                          Body=content.encode("utf-8"),
                          ContentType="text/csv" if sub_path.endswith(".csv") else "application/json")
            return True
        except Exception:
            pass
    return False


def load_batch_file(batch_id: str, sub_path: str) -> str:
    """Load a batch file from S3. Returns content string or empty string."""
    s3_key = f"batches/{batch_id}/{sub_path}"
    s3 = _get_s3()
    if s3:
        try:
            resp = s3.get_object(Bucket=S3_BUCKET, Key=s3_key)
            return resp["Body"].read().decode("utf-8")
        except Exception:
            pass
    return ""


def sync_batch_to_s3(batch_id: str, local_path):
    """Sync an entire local batch directory to S3."""
    import os
    from pathlib import Path
    local = Path(local_path) if not isinstance(local_path, Path) else local_path
    batch_dir = local / batch_id
    if not batch_dir.exists():
        return False
    s3 = _get_s3()
    if not s3:
        return False
    try:
        for root, dirs, files in os.walk(batch_dir):
            for f in files:
                fpath = Path(root) / f
                rel = fpath.relative_to(batch_dir)
                s3_key = f"batches/{batch_id}/{rel.as_posix()}"
                s3.put_object(Bucket=S3_BUCKET, Key=s3_key,
                              Body=fpath.read_bytes(),
                              ContentType="text/csv" if f.endswith(".csv") else "application/json")
        return True
    except Exception:
        return False


def load_batch_from_s3(batch_id: str, local_path):
    """Load batch files from S3 into local directory (if not already present locally)."""
    from pathlib import Path
    local = Path(local_path) if not isinstance(local_path, Path) else local_path
    batch_dir = local / batch_id
    s3 = _get_s3()
    if not s3:
        return False
    try:
        prefix = f"batches/{batch_id}/"
        resp = s3.list_objects_v2(Bucket=S3_BUCKET, Prefix=prefix)
        for obj in resp.get("Contents", []):
            key = obj["Key"]
            rel_path = key[len(prefix):]
            local_file = batch_dir / rel_path
            # Only download if local doesn't exist or is older
            if not local_file.exists():
                local_file.parent.mkdir(parents=True, exist_ok=True)
                data = s3.get_object(Bucket=S3_BUCKET, Key=key)["Body"].read()
                local_file.write_bytes(data)
        return True
    except Exception:
        return False
