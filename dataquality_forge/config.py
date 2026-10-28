import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
STORAGE_DIR = Path(os.getenv("STORAGE_DIR", DATA_DIR / "storage"))
REPORTS_DIR = Path(os.getenv("REPORTS_DIR", DATA_DIR / "reports"))
DB_PATH = Path(os.getenv("DB_PATH", DATA_DIR / "dataquality.db"))

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_PATH}")
MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "100"))
MAX_UPLOAD_BYTES = MAX_UPLOAD_SIZE_MB * 1024 * 1024
ALLOWED_EXTENSIONS = {".csv", ".tsv", ".json", ".jsonl", ".parquet"}

STORAGE_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)
