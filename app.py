"""Application entry point."""
import dash
import dash_bootstrap_components as dbc

from callbacks.register import register_callbacks
from config import DEBUG, PORT, active_data_source, runtime_host
from layout import create_layout
from sample_manager import discover_samples, sample_name_map

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

sample_choices = discover_samples()
if not sample_choices:
    raise RuntimeError(
        f"No samples found for DATA_SOURCE={active_data_source()!r}. "
        "For local mode, place sample folders inside sample_data/. "
        "For GCS mode, set DATA_SOURCE=gcs, GCS_BUCKET, and GCS_PREFIX."
    )

app.layout = create_layout(sample_choices, sample_name_map(sample_choices))
register_callbacks(app)

if __name__ == "__main__":
    print(f"Starting dashboard with DATA_SOURCE={active_data_source()}")
    app.run(host=runtime_host(), port=PORT, debug=DEBUG)
