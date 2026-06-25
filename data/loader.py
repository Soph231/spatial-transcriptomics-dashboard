"""Unified local/GCS data loading with sample-level caching."""
from __future__ import annotations

import base64
import io
import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import pandas as pd
from PIL import Image

from config import CACHE_MAXSIZE, EXPRESSION_CANDIDATES, GCS_BUCKET, GCS_PREFIX, LOCAL_DATA_ROOT, active_data_source


@dataclass(frozen=True)
class SampleData:
    cluster_df: pd.DataFrame
    hires_img_base64: str
    img_width: int
    img_height: int
    enrichment_data: dict[str, pd.DataFrame]
    cluster_ids: list[str]
    pathway_map: dict[str, list[str]]
    expression_df: pd.DataFrame
    gene_descriptions: dict[str, str]

_storage_client = None
_bucket = None


def _read_local_csv(path: Path, **kwargs) -> pd.DataFrame:
    return pd.read_csv(path, **kwargs)


def _read_local_json(path: Path) -> dict:
    with open(path, "r") as f:
        return json.load(f)


def _image_to_base64(image: Image.Image) -> tuple[str, tuple[int, int]]:
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/png;base64,{encoded}", image.size


def _read_local_image_as_base64(path: Path) -> tuple[str, tuple[int, int]]:
    return _image_to_base64(Image.open(path))


def _get_gcs_bucket():
    global _storage_client, _bucket
    if _bucket is None:
        from google.cloud import storage
        _storage_client = storage.Client()
        _bucket = _storage_client.bucket(GCS_BUCKET)
    return _bucket


def _read_gcs_csv(path: str, **kwargs) -> pd.DataFrame:
    blob = _get_gcs_bucket().blob(path)
    return pd.read_csv(io.BytesIO(blob.download_as_bytes()), **kwargs)


def _read_gcs_json(path: str) -> dict:
    blob = _get_gcs_bucket().blob(path)
    return json.loads(blob.download_as_bytes())


def _read_gcs_image_as_base64(path: str) -> tuple[str, tuple[int, int]]:
    blob = _get_gcs_bucket().blob(path)
    return _image_to_base64(Image.open(io.BytesIO(blob.download_as_bytes())))


def _gcs_blob_exists(path: str) -> bool:
    return _get_gcs_bucket().blob(path).exists()


def _assemble_sample(cluster_df, scale_factors, hires_img_base64, img_width, img_height, enrichment_data, expression_df, gene_descriptions) -> SampleData:
    cluster_df = cluster_df.copy()
    cluster_df["px_col"] *= scale_factors["tissue_hires_scalef"]
    cluster_df["px_row"] *= scale_factors["tissue_hires_scalef"]
    pathway_map = {cid: df["Term"].tolist() for cid, df in enrichment_data.items() if not df.empty and "Term" in df.columns}
    return SampleData(cluster_df, hires_img_base64, img_width, img_height, enrichment_data, list(enrichment_data.keys()), pathway_map, expression_df, gene_descriptions)


def _load_local_sample(sample_name: str) -> SampleData:
    base_path = LOCAL_DATA_ROOT / sample_name
    if not base_path.exists():
        raise FileNotFoundError(f"Could not find sample folder: {base_path}")
    cluster_df = _read_local_csv(base_path / "cluster_assignments.csv", index_col=0)
    scale_factors = _read_local_json(base_path / "spatial" / "scale_factors.json")
    hires_img_base64, (img_width, img_height) = _read_local_image_as_base64(base_path / "spatial" / "hires.png")
    enrichment_data = {}
    enrichment_dir = base_path / "enrichment_results"
    if enrichment_dir.exists():
        for csv_path in sorted(enrichment_dir.glob("*.csv")):
            if csv_path.name.startswith("._"):
                continue
            cid = csv_path.stem.replace("cluster_", "")
            try:
                enrichment_data[cid] = _read_local_csv(csv_path)
            except UnicodeDecodeError:
                enrichment_data[cid] = _read_local_csv(csv_path, encoding="latin1")
    expression_path = next((base_path / f for f in EXPRESSION_CANDIDATES if (base_path / f).exists()), None)
    if expression_path is None:
        raise FileNotFoundError(f"No expression matrix found in {base_path}.")
    expression_df = _read_local_csv(expression_path, index_col=0)
    try:
        gene_descriptions = _read_local_csv(base_path / "gene_descriptions.csv").set_index("gene")["description"].to_dict()
    except Exception:
        gene_descriptions = {}
    return _assemble_sample(cluster_df, scale_factors, hires_img_base64, img_width, img_height, enrichment_data, expression_df, gene_descriptions)


def _load_gcs_sample(sample_name: str) -> SampleData:
    base_path = f"{GCS_PREFIX}/{sample_name}"
    cluster_df = _read_gcs_csv(f"{base_path}/cluster_assignments.csv", index_col=0)
    scale_factors = _read_gcs_json(f"{base_path}/spatial/scale_factors.json")
    hires_img_base64, (img_width, img_height) = _read_gcs_image_as_base64(f"{base_path}/spatial/hires.png")
    enrichment_data = {}
    enrichment_prefix = f"{base_path}/enrichment_results/"
    _get_gcs_bucket()
    for blob in list(_storage_client.list_blobs(GCS_BUCKET, prefix=enrichment_prefix)):
        name = Path(blob.name).name
        if blob.name.endswith(".csv") and not name.startswith("._"):
            cid = name.replace("cluster_", "").replace(".csv", "")
            try:
                enrichment_data[cid] = _read_gcs_csv(blob.name)
            except UnicodeDecodeError:
                enrichment_data[cid] = _read_gcs_csv(blob.name, encoding="latin1")
    expression_path = None
    for filename in EXPRESSION_CANDIDATES:
        candidate = f"{base_path}/{filename}"
        if _gcs_blob_exists(candidate):
            expression_path = candidate
            break
    if expression_path is None:
        raise FileNotFoundError(f"No expression matrix found in gs://{GCS_BUCKET}/{base_path}.")
    expression_df = _read_gcs_csv(expression_path, index_col=0)
    try:
        gene_descriptions = _read_gcs_csv(f"{base_path}/gene_descriptions.csv").set_index("gene")["description"].to_dict()
    except Exception:
        gene_descriptions = {}
    return _assemble_sample(cluster_df, scale_factors, hires_img_base64, img_width, img_height, enrichment_data, expression_df, gene_descriptions)


@lru_cache(maxsize=CACHE_MAXSIZE)
def load_sample_resources(sample_name: str) -> SampleData:
    source = active_data_source()
    print(f"🔄 Loading sample: {sample_name} from {source}")
    sample = _load_local_sample(sample_name) if source == "local" else _load_gcs_sample(sample_name)
    print(f"✅ Loaded {sample_name}: expression={sample.expression_df.shape}, clusters={sample.cluster_df.shape}")
    return sample


def clear_sample_cache() -> None:
    load_sample_resources.cache_clear()
