import hashlib
import os
import uuid
from pathlib import Path
from typing import Tuple, Optional
import pandas as pd
import duckdb
from dataquality_forge.config import STORAGE_DIR, MAX_UPLOAD_BYTES, ALLOWED_EXTENSIONS


class StorageError(Exception):
    pass


def compute_checksum(file_path: Path) -> str:
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def save_upload_file(file_content: bytes, original_filename: str) -> Tuple[Path, str, str, int]:
    ext = Path(original_filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise StorageError(f"Unsupported extension: {ext}. Allowed: {ALLOWED_EXTENSIONS}")

    size = len(file_content)
    if size > MAX_UPLOAD_BYTES:
        raise StorageError(f"File size {size} exceeds maximum limit of {MAX_UPLOAD_BYTES} bytes")

    safe_stem = "".join(c for c in Path(original_filename).stem if c.isalnum() or c in ("-", "_")) or "dataset"
    unique_name = f"{safe_stem}_{uuid.uuid4().hex[:8]}{ext}"
    dest_path = (STORAGE_DIR / unique_name).resolve()

    if not str(dest_path).startswith(str(STORAGE_DIR.resolve())):
        raise StorageError("Path traversal detected")

    with open(dest_path, "wb") as f:
        f.write(file_content)

    checksum = compute_checksum(dest_path)
    fmt = ext.lstrip(".")
    if fmt == "tsv":
        fmt = "csv"
    return dest_path, fmt, checksum, size


def load_dataset_dataframe(file_path: str, limit: Optional[int] = None) -> pd.DataFrame:
    p = Path(file_path)
    if not p.exists():
        raise FileNotFoundError(f"Dataset file not found: {file_path}")

    ext = p.suffix.lower()
    if ext == ".csv":
        return pd.read_csv(p, nrows=limit)
    elif ext == ".tsv":
        return pd.read_csv(p, sep="\t", nrows=limit)
    elif ext == ".parquet":
        df = pd.read_parquet(p)
        return df.head(limit) if limit else df
    elif ext == ".jsonl":
        return pd.read_json(p, lines=True, nrows=limit)
    elif ext == ".json":
        df = pd.read_json(p)
        return df.head(limit) if limit else df
    else:
        raise ValueError(f"Unsupported format: {ext}")


def get_duckdb_relation(con: duckdb.DuckDBPyConnection, file_path: str):
    p = Path(file_path).as_posix()
    ext = Path(file_path).suffix.lower()
    if ext in (".csv", ".tsv"):
        return con.read_csv(p, auto_detect=True)
    elif ext == ".parquet":
        return con.read_parquet(p)
    elif ext in (".json", ".jsonl"):
        return con.read_json(p)
    else:
        raise ValueError(f"Unsupported format: {ext}")
