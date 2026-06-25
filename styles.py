"""Reusable inline styles for the dashboard layout."""
COLORS = {
    "navy": "#14274E",
    "light": "#F1F6F9",
    "middle": "#d8e2e8",
    "right": "#9BA4B4",
    "muted": "#6c757d",
}

HEADER_STYLE = {"backgroundColor": COLORS["navy"], "paddingTop": "20px", "paddingBottom": "20px"}
TITLE_STYLE = {"textAlign": "center", "marginBottom": "5px", "color": COLORS["light"]}
SUBTITLE_STYLE = {"textAlign": "center", "marginTop": "0", "marginBottom": "0px", "color": COLORS["light"]}
LABEL_STYLE = {"fontWeight": "bold", "marginBottom": "5px", "marginTop": "20px", "marginLeft": "10px", "color": COLORS["navy"]}
DROPDOWN_STYLE = {"width": "100%"}
DROPDOWN_ROW_STYLE = {"display": "flex", "width": "100%", "gap": "15px", "alignItems": "flex-start"}
SAMPLE_CONTROL_STYLE = {"flex": "2", "minWidth": "0"}
CLUSTER_CONTROL_STYLE = {"flex": "1", "minWidth": "0"}
FOOTER_STYLE = {"position": "fixed", "bottom": "0", "right": "0", "width": "25%", "alignItems": "center", "textAlign": "center", "backgroundColor": "#f8f9fa", "padding": "10px", "fontSize": "12px", "color": COLORS["muted"], "borderRadius": "8px"}
