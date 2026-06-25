# Cancer Gene Expression Dashboard

A modular Python Dash application for exploring spatial gene expression and pathway enrichment in breast cancer Visium data.

## Structure

```text
app.py                  # Dash entry point
config.py               # local/GCS configuration
layout.py               # dashboard layout
styles.py               # reusable style dictionaries
sample_manager.py       # sample discovery and friendly names
data/loader.py          # local/GCS loading + sample cache
callbacks/register.py   # Dash callbacks
assets/                 # CSS/static assets
sample_data/            # optional local demo samples
```

## Run locally

Copy your `assets/` and `sample_data/` folders into this project, then run:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:8050`.

## Run with Google Cloud Storage

```bash
DATA_SOURCE=gcs GCS_BUCKET=cancer-dash-processed-samples GCS_PREFIX=processed_samples python app.py
```

For Cloud Run, use `requirements-gcs.txt` and the included Dockerfile.

## Notes

- Local mode does not require `google-cloud-storage`.
- Samples are discovered automatically.
- The data loader caches loaded samples to reduce repeated CSV/image reads across callbacks.
