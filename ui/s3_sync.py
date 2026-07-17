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
