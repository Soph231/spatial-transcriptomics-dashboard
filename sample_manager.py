"""Sample discovery and readable sample labels."""
from config import GCS_BUCKET, GCS_PREFIX, LOCAL_DATA_ROOT, active_data_source


def format_sample_label(sample_name: str, index: int = 0) -> str:
    """
    Create a readable label from the sample folder name.

    Example:
        GSM6177599_NYU_BRCA0_Vis_processed_Analyzed2
            -> GSM6177599 NYU BRCA0
    """
    parts = [p for p in sample_name.split("_") if p]

    # Use the first three parts if available
    if len(parts) >= 3:
        return " ".join(parts[:3])

    # Fallback
    return sample_name.replace("_", " ") or f"Sample {index + 1}"


def discover_local_samples() -> list[str]:
    if not LOCAL_DATA_ROOT.exists():
        return []
    samples = []
    for sample_dir in sorted(LOCAL_DATA_ROOT.iterdir()):
        if not sample_dir.is_dir() or sample_dir.name.startswith("."):
            continue
        if (sample_dir / "cluster_assignments.csv").exists() and (sample_dir / "spatial").exists():
            samples.append(sample_dir.name)
    return samples


def discover_gcs_samples() -> list[str]:
    from google.cloud import storage
    client = storage.Client()
    prefix = f"{GCS_PREFIX}/"
    iterator = client.list_blobs(GCS_BUCKET, prefix=prefix, delimiter="/")
    list(iterator)
    samples = []
    for pref in iterator.prefixes:
        sample = pref.rstrip("/").split("/")[-1]
        if sample and not sample.startswith("."):
            samples.append(sample)
    return sorted(samples)


def discover_samples() -> list[str]:
    source = active_data_source()
    if source == "local":
        return discover_local_samples()
    if source == "gcs":
        return discover_gcs_samples()
    raise ValueError("Active data source must be 'local' or 'gcs'.")


def sample_name_map(samples: list[str]) -> dict[str, str]:
    return {sample: format_sample_label(sample, i) for i, sample in enumerate(samples)}
