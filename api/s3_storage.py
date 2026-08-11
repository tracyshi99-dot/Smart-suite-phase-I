"""
S3 Storage Layer for Smart Suite API
=====================================
All data persistence goes through S3. Lambda /tmp is only used for temporary processing.
Bucket: smartsuite-sync-data
Prefix: smartsuite/output/{batch_id}/{step}/

Functions:
- read_csv(batch_id, step, filename) → DataFrame
- write_csv(batch_id, step, filename, df)
- read_json(batch_id, step, filename) → dict
- write_json(batch_id, step, filename, data)
- archive_items(batch_id, step, filename, df_to_archive)
- get_archived(batch_id, step, filename) → DataFrame
- restore_items(batch_id, step, filename, items_to_restore) → DataFrame
- list_history(batch_id, step) → list of file metadata
"""
import os
import json
import io
import boto3
import pandas as pd
from datetime import datetime
from pathlib import Path

S3_BUCKET = os.environ.get("SMARTSUITE_S3_BUCKET", "smartsuite-sync-data")
S3_PREFIX = os.environ.get("SMARTSUITE_S3_PREFIX", "smartsuite/")
REGION = "us-east-1"

_client = None

def _get_s3():
    global _client
    if _client is None:
        _client = boto3.client("s3", region_name=REGION)
    return _client


def _s3_key(batch_id: str, step: str, filename: str) -> str:
    """Build S3 key: smartsuite/output/{batch_id}/{step}/{filename}"""
    return f"{S3_PREFIX}output/{batch_id}/{step}/{filename}"


def read_csv(batch_id: str, step: str, filename: str) -> pd.DataFrame:
    """Read a CSV file from S3. Returns empty DataFrame if not found."""
    key = _s3_key(batch_id, step, filename)
    try:
        s3 = _get_s3()
        obj = s3.get_object(Bucket=S3_BUCKET, Key=key)
        return pd.read_csv(io.BytesIO(obj["Body"].read()), encoding="utf-8-sig", on_bad_lines="skip")
    except Exception:
        return pd.DataFrame()


def write_csv(batch_id: str, step: str, filename: str, df: pd.DataFrame):
    """Write a DataFrame as CSV to S3."""
    key = _s3_key(batch_id, step, filename)
    s3 = _get_s3()
    csv_buffer = io.BytesIO()
    df.to_csv(csv_buffer, index=False, encoding="utf-8-sig")
    csv_buffer.seek(0)
    s3.put_object(Bucket=S3_BUCKET, Key=key, Body=csv_buffer.getvalue())


def read_json(batch_id: str, step: str, filename: str) -> dict:
    """Read a JSON file from S3. Returns empty dict if not found."""
    key = _s3_key(batch_id, step, filename)
    try:
        s3 = _get_s3()
        obj = s3.get_object(Bucket=S3_BUCKET, Key=key)
        return json.loads(obj["Body"].read().decode("utf-8"))
    except Exception:
        return {}


def write_json(batch_id: str, step: str, filename: str, data):
    """Write JSON data to S3."""
    key = _s3_key(batch_id, step, filename)
    s3 = _get_s3()
    body = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
    s3.put_object(Bucket=S3_BUCKET, Key=key, Body=body)


def archive_items(batch_id: str, step: str, filename: str, df_to_archive: pd.DataFrame):
    """Move items to _archived.csv (append). Returns updated archive."""
    archive_filename = "_archived.csv"
    existing_archive = read_csv(batch_id, step, archive_filename)
    
    # Add timestamp
    df_to_archive = df_to_archive.copy()
    df_to_archive["_archived_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # Append to archive
    if existing_archive.empty:
        new_archive = df_to_archive
    else:
        new_archive = pd.concat([existing_archive, df_to_archive], ignore_index=True)
    
    write_csv(batch_id, step, archive_filename, new_archive)
    return new_archive


def get_archived(batch_id: str, step: str) -> pd.DataFrame:
    """Get all archived items for a step."""
    return read_csv(batch_id, step, "_archived.csv")


def restore_items(batch_id: str, step: str, main_filename: str, queries_to_restore: list) -> pd.DataFrame:
    """Restore items from archive back to main file. Returns updated main df."""
    archive_df = read_csv(batch_id, step, "_archived.csv")
    main_df = read_csv(batch_id, step, main_filename)
    
    if archive_df.empty or not queries_to_restore:
        return main_df
    
    # Find items to restore
    key_col = "ai_query" if "ai_query" in archive_df.columns else archive_df.columns[0]
    restore_mask = archive_df[key_col].isin(queries_to_restore)
    df_to_restore = archive_df[restore_mask].drop(columns=["_archived_at"], errors="ignore")
    remaining_archive = archive_df[~restore_mask]
    
    # Merge back to main
    if main_df.empty:
        merged = df_to_restore
    else:
        merged = pd.concat([main_df, df_to_restore], ignore_index=True)
        if key_col in merged.columns:
            merged = merged.drop_duplicates(subset=[key_col], keep="last")
    
    # Save both
    write_csv(batch_id, step, main_filename, merged)
    write_csv(batch_id, step, "_archived.csv", remaining_archive)
    
    return merged


def list_files(batch_id: str, step: str) -> list:
    """List all files in a step directory."""
    prefix = _s3_key(batch_id, step, "")
    s3 = _get_s3()
    try:
        response = s3.list_objects_v2(Bucket=S3_BUCKET, Prefix=prefix)
        files = []
        for obj in response.get("Contents", []):
            filename = obj["Key"][len(prefix):]
            if filename and not filename.startswith("."):
                files.append({
                    "filename": filename,
                    "size": obj["Size"],
                    "last_modified": obj["LastModified"].isoformat(),
                })
        return files
    except Exception:
        return []
