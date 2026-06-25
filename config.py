"""Application configuration for local and Google Cloud Storage deployments."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
LOCAL_DATA_ROOT = Path(os.environ.get("LOCAL_DATA_ROOT", BASE_DIR / "sample_data"))
GCS_BUCKET = os.environ.get("GCS_BUCKET", "cancer-dash-processed-samples")
GCS_PREFIX = os.environ.get("GCS_PREFIX", "processed_samples").strip("/")
DATA_SOURCE = os.environ.get("DATA_SOURCE", "auto").strip().lower()

HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", "8050"))
DEBUG = os.environ.get("DEBUG", "false").lower() in {"1", "true", "yes", "y"}
CACHE_MAXSIZE = int(os.environ.get("CACHE_MAXSIZE", "4"))

EXPRESSION_CANDIDATES = [
    "expression_100_hvg.csv",
    "expression_250_hvg.csv",
    "expression_500_hvg.csv",
    "expression_hvg.csv",
    "expression.csv",
]


def has_local_samples() -> bool:
    if not LOCAL_DATA_ROOT.exists():
        return False
    return any(
        p.is_dir()
        and not p.name.startswith(".")
        and (p / "cluster_assignments.csv").exists()
        and (p / "spatial").exists()
        for p in LOCAL_DATA_ROOT.iterdir()
    )


def active_data_source() -> str:
    if DATA_SOURCE in {"local", "gcs"}:
        return DATA_SOURCE
    if DATA_SOURCE != "auto":
        raise ValueError("DATA_SOURCE must be 'auto', 'local', or 'gcs'.")
    return "local" if has_local_samples() else "gcs"


def runtime_host() -> str:
    if os.environ.get("PORT") or active_data_source() == "gcs":
        return os.environ.get("HOST", "0.0.0.0")
    return HOST
