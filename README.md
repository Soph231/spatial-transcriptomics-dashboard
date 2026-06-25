# Cancer Gene Expression Dashboard
![Screenshot](https://github.com/Soph231/spatial-transcriptomics-dashboard/blob/main/screenshot/cancer_expression_dashboard.png)

A modular Python Dash application for exploring spatial gene expression and pathway enrichment in breast cancer tissue.
The dashboard was developed using Visium spatial transcriptomics data from breast cancer samples and provides tools for investigating cluster-specific pathways and spatial patterns of gene expression.
## Features

    - Interactive spatial gene expression visualization
    - Cluster-specific pathway enrichment analysis
    - Differential expression summaries
    - Multiple sample support
    - Docker deployment files
    - Representative sample dataset included


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

## Dataset

Dataset: GSE203612
Platform: 10x Genomics Visium Spatial Transcriptomics

The data were generated and published by the original authors. This repository focuses on the processing, 
visualization, and interactive exploration of the data using Python and Dash. A representative sample dataset 
is included to demonstrate the expected file structure, while the complete processed dataset is stored 
externally.
This project uses breast cancer spatial transcriptomics data generated using the 1
0x Genomics Visium platform.

Source:

* GEO accession: [**GSE203612**](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE203612)
## Purpose
This repository was developed as a portfolio and learning project demonstrating how publicly 
available spatial transcriptomics data can be processed and explored through 
interactive dashboards. The emphasis is on data visualization, pathway enrichment analysis,
and deployment rather than on reproducing the original biological study.

## Installation

Clone the repository:

```bash
git clone https://github.com/soph213/spatial-transcriptomics-dashboard.git
cd spatial-transcriptomics-dashboard
```


## Run locally

Copy your `assets/` and `sample_data/` folders into this project, then:

Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate
```
Install dependencies:
```
pip install -r requirements.txt
```
Run the application
```
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

## Live Dashboard

A deployed version of the [dashboard](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE203612) is available online.

## License

This repository is provided for educational and research purposes.

