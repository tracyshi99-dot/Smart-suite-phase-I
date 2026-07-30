"""
S3 Sync Module for Smart Suite
================================
Provides transparent S3 sync layer so that:
- Streamlit Cloud can read/write data to S3 (using AWS creds from secrets)
- EC2 cron can read/write data to S3 (using Instance Profile)
- Both environments share the same data

Usage:
    from s3_sync import s3_sync, pull_from_s3, push_to_s3, sync_file_to_s3

Architecture:
    Local output/ ←→ S3 bucket (smartsuite-data-830279064391)
    - On app startup: pull latest from S3
    - After each write operation: push changed files to S3
    - EC2 cron: reads from S3, writes results back to S3
"""
import os
import json
import logging
import threading
from pathlib import Path
from datetime import datetime

log = logging.getLogger("s3_sync")

# Configuration
S3_BUCKET = "smartsuite-sync-data"  # Use existing bucket from Streamlit Cloud secrets
S3_PREFIX = "smartsuite/"  # prefix inside bucket
REGION = "us-east-1"

# Determine base paths
_BASE = Path(__file__).parent.parent
OUTPUT_PATH = _BASE / "output"
INPUT_PATH = _BASE / "input"

# Track sync state
_sync_lock = threading.Lock()
_last_sync_time = None


def _get_s3_client():
    """Get S3 client. Works on both Streamlit Cloud (secrets) and EC2 (Instance Profile)."""
    import boto3
    
    # Try Streamlit secrets first (for Streamlit Cloud)
    try:
        import streamlit as st
        if hasattr(st, "secrets") and "aws" in st.secrets:
            aws_secrets = st.secrets["aws"]
            # Support both naming conventions
            access_key = aws_secrets.get("access_key_id") or aws_secrets.get("AWS_ACCESS_KEY_ID", "")
            secret_key = aws_secrets.get("secret_access_key") or aws_secrets.get("AWS_SECRET_ACCESS_KEY", "")
            region = aws_secrets.get("region") or aws_secrets.get("AWS_DEFAULT_REGION", REGION)
            # Also check for bucket override
            global S3_BUCKET
            bucket_override = aws_secrets.get("SMARTSUITE_S3_BUCKET", "")
            if bucket_override:
                S3_BUCKET = bucket_override
            if access_key and secret_key:
                return boto3.client(
                    "s3",
                    region_name=region,
                    aws_access_key_id=access_key,
                    aws_secret_access_key=secret_key,
                )
    except Exception:
        pass
    
    # Fallback to default credentials (EC2 Instance Profile or local ~/.aws)
    import boto3
    return boto3.client("s3", region_name=REGION)


def pull_from_s3(prefix_filter: str = None, force: bool = False):
    """Pull latest data from S3 to local output/ directory.
    
    Args:
        prefix_filter: Only pull files matching this prefix (e.g., "output/requests/")
        force: Pull even if recently synced
    """
    global _last_sync_time
    
    # Skip if recently synced (within 30 seconds) unless forced
    if not force and _last_sync_time:
        elapsed = (datetime.now() - _last_sync_time).total_seconds()
        if elapsed < 30:
            return
    
    try:
        s3 = _get_s3_client()
        s3_prefix = S3_PREFIX
        if prefix_filter:
            s3_prefix += prefix_filter
        
        paginator = s3.get_paginator("list_objects_v2")
        pages = paginator.paginate(Bucket=S3_BUCKET, Prefix=s3_prefix)
        
        count = 0
        for page in pages:
            for obj in page.get("Contents", []):
                s3_key = obj["Key"]
                # Convert S3 key to local path
                relative_path = s3_key[len(S3_PREFIX):]  # Remove "smartsuite/" prefix
                local_path = _BASE / relative_path
                
                # Only download if S3 is newer
                if local_path.exists():
                    local_mtime = datetime.fromtimestamp(local_path.stat().st_mtime)
                    s3_mtime = obj["LastModified"].replace(tzinfo=None)
                    if local_mtime >= s3_mtime:
                        continue
                
                # Download
                local_path.parent.mkdir(parents=True, exist_ok=True)
                s3.download_file(S3_BUCKET, s3_key, str(local_path))
                count += 1
        
        _last_sync_time = datetime.now()
        if count > 0:
            log.info(f"Pulled {count} files from S3")
        return count
        
    except Exception as e:
        log.warning(f"S3 pull failed: {e}")
        return 0


def push_to_s3(local_path: str = None, prefix_filter: str = None):
    """Push local files to S3.
    
    Args:
        local_path: Specific file to push (absolute path)
        prefix_filter: Push all files under this relative path (e.g., "output/batch_003/")
    """
    try:
        s3 = _get_s3_client()
        count = 0
        
        if local_path:
            # Push single file
            p = Path(local_path)
            if p.exists() and p.is_file():
                relative = p.relative_to(_BASE)
                s3_key = S3_PREFIX + str(relative).replace("\\", "/")
                s3.upload_file(str(p), S3_BUCKET, s3_key)
                count = 1
        elif prefix_filter:
            # Push all files under prefix
            local_dir = _BASE / prefix_filter
            if local_dir.exists():
                for f in local_dir.rglob("*"):
                    if f.is_file() and not f.name.startswith("."):
                        relative = f.relative_to(_BASE)
                        s3_key = S3_PREFIX + str(relative).replace("\\", "/")
                        s3.upload_file(str(f), S3_BUCKET, s3_key)
                        count += 1
        else:
            # Push entire output directory
            for f in OUTPUT_PATH.rglob("*"):
                if f.is_file() and not f.name.startswith("."):
                    relative = f.relative_to(_BASE)
                    s3_key = S3_PREFIX + str(relative).replace("\\", "/")
                    s3.upload_file(str(f), S3_BUCKET, s3_key)
                    count += 1
        
        if count > 0:
            log.info(f"Pushed {count} files to S3")
        return count
        
    except Exception as e:
        log.warning(f"S3 push failed: {e}")
        return 0


def sync_file_to_s3(file_path):
    """Push a single file to S3 (call after any write operation).
    Runs in background thread to not block UI.
    """
    def _do_push():
        try:
            push_to_s3(local_path=str(file_path))
        except Exception:
            pass
    
    t = threading.Thread(target=_do_push, daemon=True)
    t.start()


def sync_directory_to_s3(dir_path: str):
    """Push entire directory to S3 in background."""
    def _do_push():
        try:
            relative = Path(dir_path).relative_to(_BASE)
            push_to_s3(prefix_filter=str(relative).replace("\\", "/"))
        except Exception:
            pass
    
    t = threading.Thread(target=_do_push, daemon=True)
    t.start()


def full_sync():
    """Full bidirectional sync: pull from S3, then push local changes."""
    pull_from_s3(force=True)
    push_to_s3()


def initial_pull():
    """Called on app startup to get latest data from S3."""
    log.info("Initial S3 pull starting...")
    count = pull_from_s3(force=True)
    log.info(f"Initial S3 pull complete: {count} files updated")
    return count


# --- Integration helper for existing code ---

def patch_mark_data_changed(original_func):
    """Decorator to add S3 sync after mark_data_changed() calls."""
    def wrapper(*args, **kwargs):
        result = original_func(*args, **kwargs)
        # After data changes, push output to S3
        sync_directory_to_s3(str(OUTPUT_PATH))
        return result
    return wrapper
