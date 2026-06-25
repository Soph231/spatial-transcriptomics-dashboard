"""Dash callback registration."""
import dash
from dash import html, Input, Output
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from data.loader import load_sample_resources


def tuple_load_sample_resources(sample_path):
    sample = load_sample_resources(sample_path)
    return (
        sample.cluster_df,
        sample.hires_img_base64,
        sample.img_width,
        sample.img_height,
        sample.enrichment_data,
        sample.cluster_ids,
        sample.pathway_map,
        sample.expression_df,
        sample.gene_descriptions,
    )


def register_callbacks(app):
    @app.callback(
        Output("loaded-sample-store", "data"),
        Output("sample-output", "children"),
        Output("loading-flag-store", "data"),  # for greying while loading data
        Input("sample-dropdown", "value")
    )
    def update_sample_store(selected_sample):
        if not selected_sample:
            return dash.no_update, "Select a sample", True

        # Set loading flag first
        loading_msg = html.Span("⏳ Loading sample...", style={"font-size": "12px", "color": "gray"})

        # Return early placeholder (optional)
        print("🔄 Starting to load sample...")
        (
            cluster_df,
            _,
            _,
            _,
            _,
            cluster_ids,
            _,
            _,
            _
        ) = tuple_load_sample_resources(selected_sample)

        summary = html.Span(
            f"✅ Loaded: {len(cluster_df)} spots across {len(cluster_ids)} clusters",
            style={"color": "green", "font-size": "12px"}
        )

        return selected_sample, summary, False  # ✅ Done loading

    
    # update intial disabled dropdowns while sample loading
    @app.callback(
        Output("sample-dropdown", "disabled"),
        Output("cluster-dropdown", "disabled"),
        Output("pathway-dropdown", "disabled"),
        Output("gene-dropdown", "disabled"),
        Input("loading-flag-store", "data")
    )
    def toggle_all_dropdowns_while_loading(loading_flag):
        return loading_flag, loading_flag, loading_flag, loading_flag

    # update umap    
    @app.callback(
        Output("umap-plot", "figure"),
        Input("loaded-sample-store", "data")
    )
    def update_umap(sample_path):
        if not sample_path:
            return go.Figure()

        (
            cluster_df,
            _,
            _,
            _,
            _,
            _,
            _,
            _,
            _  # gene_descriptions
        ) = tuple_load_sample_resources(sample_path)

        # Ensure UMAP columns exist
        if "UMAP_1" not in cluster_df.columns or "UMAP_2" not in cluster_df.columns:
            return go.Figure()

        fig = px.scatter(
            x=cluster_df["UMAP_1"],
            y=cluster_df["UMAP_2"],
            color=cluster_df["leiden"].astype(str),
            labels={"color": "Cluster"},
            title="UMAP of Clusters"
        )

        fig.update_layout(
            title="Uniform Manifold Approximation and Projection (UMAP) of Clusters",
            height=300,
            margin=dict(l=0, r=0, t=50, b=0),
            plot_bgcolor="white"
        )

        return fig

    '''
    # update cluster information
    @app.callback(
        Output("cluster-summary-text", "children"),
        Input("loaded-sample-store", "data")
    )
    def update_cluster_info(sample_path):
        if not sample_path:
            return "Select a sample to load cluster info."

        (
            cluster_df,
            _,
            _,
            _,
            enrichment_data,
            cluster_ids,
            pathway_map,
            _,
            _
        ) = tuple_load_sample_resources(sample_path)

        # 📊 Cluster sizes from cluster_df
        cluster_counts = cluster_df["leiden"].value_counts().sort_index()

        cluster_summary_lines = []

        for cid in cluster_ids:
            cluster_key = f"cluster_{cid}"
            cluster_spots = cluster_counts.get(cid, 0)

            enrichment_df = enrichment_data.get(cid)

            if enrichment_df is not None and not enrichment_df.empty:
                total_pathways = len(enrichment_df)
                sig_pathways = (enrichment_df["Adjusted P-value"] < 0.05).sum()
            else:
                total_pathways = 0
                sig_pathways = 0

            # 🔥 Highlight if most pathways are significant
            highlight_marker = "🔥" if total_pathways > 0 and (sig_pathways / total_pathways) > 0.5 else ""

            cluster_summary_lines.append(
                f"{highlight_marker} Cluster {cid}: {cluster_spots} spots | {sig_pathways} significant / {total_pathways} total"
            )

        cluster_summary_text = "\n".join(cluster_summary_lines)

        return html.Div([
            html.H5("Cluster Overview:"),
            html.Pre(cluster_summary_text)
        ])
    '''

    #update cluster drop-down
    @app.callback(
        Output("cluster-dropdown", "options"),
        Output("cluster-dropdown", "value"),
        Input("loaded-sample-store", "data")
    )
    def update_cluster_dropdown(sample_path):
        if not sample_path:
            return [], None

        (
            cluster_df,
            _,
            _,
            _,
            _,
            _,
            cluster_ids,
            _,
            _  # expression_df, gene_descriptions
        ) = tuple_load_sample_resources(sample_path)

        # Convert to integers for sorting (if needed)
        try:
            sorted_ids = sorted(cluster_ids, key=lambda x: int(x))
        except:
            sorted_ids = sorted(cluster_ids)

        options = [{"label": f"Cluster {cid}", "value": cid} for cid in sorted_ids]
        default_value = sorted_ids[0] if sorted_ids else None

        return options, default_value


    @app.callback(
        Output("pathway-dropdown", "options"),
        Output("pathway-dropdown", "value"),
        Input("cluster-dropdown", "value"),
        Input("significance-toggle", "value"),
        Input("loaded-sample-store", "data")
    )
    def update_pathway_dropdown(cluster_id, toggle_value, sample_path):
        if not sample_path:
            print("Select a sample to load")
            return [], []

        (
            cluster_df,
            hires_img_base64,
            img_width,
            img_height,
            enrichment_data,
            cluster_ids,
            pathway_map,
            expression_df,
            _
        ) = tuple_load_sample_resources(sample_path)

        enrichment_df = enrichment_data.get(cluster_id)

        if enrichment_df is None or enrichment_df.empty:
            return [], []

        if "significant" in toggle_value:
            filtered = enrichment_df[enrichment_df["Adjusted P-value"] < 0.05]
        else:
            filtered = enrichment_df

        if filtered.empty:
            return [], []

        options = [{"label": row["Term"], "value": row["Term"]} for _, row in filtered.iterrows()]
        default = [options[0]["value"]] if options else []

        return options, default
    # function for cluster interpretation
    def interpret_cluster_from_enrichment(enrichment_df, cluster_id=None, pval_cutoff=0.05, max_terms=5):
        """
        Interprets enriched biological themes in a cluster.

        Parameters:
        - enrichment_df: pd.DataFrame of enrichment results
        - cluster_id: str or int (optional, unused here)
        - pval_cutoff: float, threshold for adjusted p-value
        - max_terms: int, max number of themes to summarize

        Returns:
        - str interpretation summary
        """

        if enrichment_df is None or enrichment_df.empty:
            return "No enrichment results available."

        sig = enrichment_df[enrichment_df["Adjusted P-value"] < pval_cutoff]
        if sig.empty:
            return "No significantly enriched pathways detected."

        themes = {
            "proliferation": ["E2F", "G2M", "MYC", "MITOTIC", "CELL_CYCLE", "DNA_REPLICATION"],
            "immune activation": ["INTERFERON", "INFLAMMATORY", "ALLOGRAFT", "IL2", "IL6", "TNFA", "COMPLEMENT", "ANTIGEN", "IMMUNE", "T_CELL", "B_CELL", "NK_CELL", "CYTOKINE"],
            "angiogenesis / hypoxia": ["ANGIOGENESIS", "VEGF", "HYPOXIA", "ENDOTHELIAL", "VASCULATURE", "NEOVASCULARIZATION"],
            "hormonal signaling": ["ESTROGEN", "ANDROGEN", "HORMONE", "RECEPTOR", "PROGESTERONE"],
            "stress response": ["P53", "DNA_REPAIR", "UV", "UNFOLDED", "OXIDATIVE", "ER_STRESS", "APOPTOSIS", "REACTIVE_OXYGEN", "STRESS", "HEAT_SHOCK"],
            "metabolic reprogramming": ["GLYCOLYSIS", "OXIDATIVE", "FATTY_ACID", "ADIPOGENESIS", "CHOLESTEROL", "MTOR", "GLUTAMINE", "LIPID", "METABOLISM", "OXPHOS", "INSULIN", "ENERGY"],
            "EMT / mesenchymal transition": ["EMT", "MYOGENESIS", "COAGULATION", "MESENCHYMAL", "TGF_BETA", "EXTRACELLULAR_MATRIX"],
            "differentiation / development": ["NOTCH", "WNT", "HEDGEHOG", "TGF_BETA", "MORPHOGEN", "DEVELOPMENT", "STEM_CELL"],
            "epigenetic regulation": ["EPIGENETIC", "METHYLATION", "CHROMATIN", "HISTONE", "POLYCOMB", "PRC2"],
            "translation / ribosome": ["RIBOSOME", "TRANSLATION", "EIF", "PROTEIN_SYNTHESIS", "SRP_DEPENDENT"],
            "apoptosis / cell death": ["APOPTOSIS", "BCL2", "CASPASE", "CELL_DEATH", "NECROSIS", "FERROPTOSIS"],
            "cell adhesion / ECM": ["INTEGRIN", "ECM", "EXTRACELLULAR_MATRIX", "MATRISOME", "CELL_ADHESION", "CADHERIN"],
            "tumor suppression": ["P53", "RB1", "TUMOR_SUPPRESSOR", "SENESCENCE", "CDKN"],
            "oncogenic signaling": ["RAS", "PI3K", "AKT", "MAPK", "EGFR", "HER2", "SRC", "JAK_STAT", "ERBB", "ABL"],
            "autophagy / lysosome": ["AUTOPHAGY", "LYSOSOME", "ENDOSOME", "MITOPHAGY", "MACROAUTOPHAGY"]
        }

        theme_scores = {}

        for theme, keywords in themes.items():
            matches = sig[sig["Term"].str.upper().apply(lambda t: any(k in t for k in keywords))]
            if not matches.empty:
                best_p = matches["Adjusted P-value"].min()
                theme_scores[theme] = {
                    "pval": best_p,
                    "terms": matches["Term"].tolist()
                }

        if not theme_scores:
            return "Significant enrichment detected, but no dominant biological theme was identified."

        ranked = sorted(theme_scores.items(), key=lambda x: x[1]["pval"])[:max_terms]

        lines = ["🧬 This cluster shows enrichment in:"]
        for theme, data in ranked:
            term_list = ", ".join(data["terms"][:3])
            lines.append(f"• {theme.title()} (e.g., {term_list})")

        return "\n".join(lines)

    # update cluster interpretation
    @app.callback(
        Output("cluster-interpretation-text", "children"),
        Input("cluster-dropdown", "value"),
        Input("loaded-sample-store", "data")
    )
    def update_interpretation_from_enrichment(cluster_id, sample_path):
        if not sample_path or not cluster_id:
            return "Select a sample and cluster to view interpretation."

        (
            cluster_df,
            hires_img_base64,
            img_width,
            img_height,
            enrichment_data,
            cluster_ids,
            pathway_map,
            expression_df,
            _
        ) = tuple_load_sample_resources(sample_path)

        enrichment_df = enrichment_data.get(cluster_id)
        if not isinstance(enrichment_df, pd.DataFrame) or enrichment_df.empty:
            return "No enrichment results available for this cluster."

        return interpret_cluster_from_enrichment(enrichment_df, cluster_id=cluster_id)

    # update for warning message when >1 pathway selected
    @app.callback(
        Output("blend-warning", "children"),
        Input("pathway-dropdown", "value"),
        Input("vis-mode", "value")
    )
    def check_pathway_blend_requirement(selected_pathways, vis_mode):
        if selected_pathways and isinstance(selected_pathways, list) and len(selected_pathways) > 1 and vis_mode != "blend":
            return html.Div("⚠️ Multiple pathways selected — please switch to 'Pathway Blend' mode.", 
                            style={'color': '#FFA500', 'font-size': '14px'})
        if selected_pathways and isinstance(selected_pathways, list) and len(selected_pathways) == 1 and vis_mode != "expression":
            return html.Div("⚠️ A single pathway selected — please switch to 'Expression Heatmap' mode.", 
                            style={'color': '#FFA500', 'font-size': '14px'})
        else:
            return ""

    # update warning message for when >1 pathway selected, we see genes of first selected pathway
    @app.callback(
        Output("pathway-warning", "children"),
        Input("pathway-dropdown", "value"),
        Input("vis-mode", "value")
    )
    def warn_genelist_pathway_blend(selected_pathways, vis_mode):
        if selected_pathways and isinstance(selected_pathways, list) and len(selected_pathways) > 1 and vis_mode == "blend":
            return html.Div("⚠️ Multiple pathways selected — Only genes from the first selected pathway are shown.", 
                            style={'color': '#FFA500', 'font-size': '14px'})
        else:
            return ""

    # update spatial overlay
    @app.callback(
        Output("spatial-overlay-plot", "figure"),
        Input("cluster-dropdown", "value"),
        Input("pathway-dropdown", "value"),
        Input("vis-mode", "value"),
        Input("loaded-sample-store", "data")
    )
    def update_spatial_overlay(cluster_id, selected_pathways, vis_mode, sample_path):
        if not selected_pathways or not sample_path:
            return go.Figure()

        (
            cluster_df,
            hires_img_base64,
            img_width,
            img_height,
            enrichment_data,
            cluster_ids,
            pathway_map,
            expression_df,
            _
        ) = tuple_load_sample_resources(sample_path)

        enrichment_df = enrichment_data.get(cluster_id)
        if enrichment_df is None or enrichment_df.empty:
            return go.Figure()

        # Prepare spatial coordinates
        df_coords = cluster_df.rename(columns={"px_col": "x", "px_row": "y"})[["x", "y"]].copy()
        df_coords["barcode"] = cluster_df.index

        fig = go.Figure()

        # If single pathway + expression mode
        if vis_mode == "expression" and len(selected_pathways) == 1:
            pathway = selected_pathways[0]
            row = enrichment_df[enrichment_df["Term"] == pathway]
            if row.empty:
                return go.Figure()

            genes = row.iloc[0]["Genes"].split(";")
            genes = [g for g in genes if g in expression_df.columns]

            if not genes:
                return go.Figure()

            expr = expression_df[genes].mean(axis=1)

            fig.add_trace(go.Scattergl(
                x=df_coords["x"],
                y=df_coords["y"],
                mode="markers",
                name=pathway,
                marker=dict(
                    size=6,
                    color=expr,
                    colorscale="inferno",
                    showscale=True,
                    colorbar=dict(title="Mean Expression")
                ),
                hovertext=[f"{pathway}<br>Expression: {v:.2f}" for v in expr],
                hoverinfo="text"
            ))

        # Else: blend mode for multiple pathways
        elif vis_mode == "blend" and len(selected_pathways) > 1:
            base_colors = {
                "red": [255, 0, 0],
                "green": [0, 255, 0],
                "blue": [0, 0, 255],
                "orange": [255, 165, 0],
                "purple": [128, 0, 128],
                "cyan": [0, 255, 255],
                "yellow": [255, 255, 0],
                "magenta": [255, 0, 255]
            }
            color_names = list(base_colors.keys())
            pathway_colors = {
                p: base_colors[color_names[i % len(color_names)]]
                for i, p in enumerate(selected_pathways)
            }

            n_spots = expression_df.shape[0]
            color_matrix = np.zeros((n_spots, 3))
            spot_expr_by_pathway = [{} for _ in range(n_spots)]

            for pathway, rgb in pathway_colors.items():
                row = enrichment_df[enrichment_df["Term"] == pathway]
                if row.empty:
                    continue

                genes = row.iloc[0]["Genes"].split(";")
                genes = [g for g in genes if g in expression_df.columns]
                if not genes:
                    continue

                expr_mean = expression_df[genes].mean(axis=1)
                norm_expr = (expr_mean - expr_mean.min()) / (expr_mean.max() - expr_mean.min() + 1e-6)
                for i, v in enumerate(norm_expr):
                    spot_expr_by_pathway[i][pathway] = v
                for j in range(3):
                    color_matrix[:, j] += norm_expr.values * rgb[j]

            color_matrix = np.clip(color_matrix, 0, 255).astype(np.uint8)
            hex_colors = ["#" + "".join(f"{val:02x}" for val in rgb) for rgb in color_matrix]

            hover_text = []
            for i, spot_expr in enumerate(spot_expr_by_pathway):
                expressed = {p: val for p, val in spot_expr.items() if val > 0.1}
                if not expressed:
                    hover_text.append("No expression")
                    continue

                sorted_expr = sorted(expressed.items(), key=lambda x: x[1], reverse=True)
                dominant = sorted_expr[0][0]
                expressed_names = ", ".join(p for p, _ in sorted_expr)
                hover_text.append(f"Pathways: {expressed_names}<br>Dominant: {dominant}")

            fig.add_trace(go.Scattergl(
                x=df_coords["x"],
                y=df_coords["y"],
                mode="markers",
                marker=dict(
                    size=6,
                    color=hex_colors,
                    opacity=0.9
                ),
                text=hover_text,
                hoverinfo="text"
            ))

            # Add legend entries
            for pathway, rgb in pathway_colors.items():
                hex_color = "#" + "".join(f"{c:02x}" for c in rgb)
                fig.add_trace(go.Scatter(
                    x=[None], y=[None],
                    mode='markers',
                    marker=dict(size=10, color=hex_color),
                    legendgroup=pathway,
                    showlegend=True,
                    name=pathway
                ))

        # Add histology image
        fig.add_layout_image(
            dict(
                source=hires_img_base64,
                xref="x", yref="y",
                x=0, y=0,
                sizex=img_width, sizey=img_height,
                sizing="stretch",
                opacity=0.25,
                layer="below"
            )
        )

        fig.update_layout(
            height=500,
            title="Spatial Pathway Overlay",
            xaxis=dict(range=[0, img_width], showgrid=False),
            yaxis=dict(range=[img_height, 0], showgrid=False, scaleanchor="x"),
            plot_bgcolor="white",
            margin=dict(l=0, r=0, t=40, b=0)
        )

        return fig
    # update gene expression plot
    @app.callback(
        Output("gene-dropdown", "options"),
        Output("gene-dropdown", "value"),
        Input("cluster-dropdown", "value"),
        Input("pathway-dropdown", "value"),
        Input("loaded-sample-store", "data")
    )
    def update_gene_dropdown(cluster_id, selected_pathways, sample_path):
        if not selected_pathways or not sample_path:
            return [], None

        (
            cluster_df,
            hires_img_base64,
            img_width,
            img_height,
            enrichment_data,
            cluster_ids,
            pathway_map,
            expression_df,
            _
        ) = tuple_load_sample_resources(sample_path)

        enrichment_df = enrichment_data.get(cluster_id)
        if enrichment_df is None or enrichment_df.empty:
            return [], None

        row = enrichment_df[enrichment_df["Term"] == selected_pathways[0]]
        if row.empty:
            return [], None

        genes = [g for g in row.iloc[0]["Genes"].split(";") if g in expression_df.columns]
        if not genes:
            return [], None

        # Sort by mean expression
        expr = expression_df[genes].values
        mean_expr = expr.mean(axis=0)
        gene_expr_pairs = sorted(zip(genes, mean_expr), key=lambda x: x[1], reverse=True)
        sorted_genes = [g for g, _ in gene_expr_pairs]

        options = [{"label": g, "value": g} for g in sorted_genes]
        return options, sorted_genes[0] if sorted_genes else ([], None)

    @app.callback(
        Output("gene-expression-plot", "figure"),
        Input("gene-dropdown", "value"),
        Input("loaded-sample-store", "data")
    )
    def plot_gene_expression(gene, sample_path):
        if not gene or not sample_path:
            return go.Figure()

        (
            cluster_df,
            hires_img_base64,
            img_width,
            img_height,
            enrichment_data,
            cluster_ids,
            pathway_map,
            expression_df,
            gene_descriptions
        ) = tuple_load_sample_resources(sample_path)

        if gene not in expression_df.columns:
            print(f"❌ Gene {gene} not in expression_df.columns") #for debug
            return go.Figure()
        print(f"🧪 Plotting {gene} for {sample_path}")
        print(f"🎯 Expression range: {expression_df[gene].min()} – {expression_df[gene].max()}")
        print(f"🖼️ Image size: {img_width}x{img_height}")
        print("📌 px_col range:", cluster_df["px_col"].min(), "-", cluster_df["px_col"].max())
        print("📌 px_row range:", cluster_df["px_row"].min(), "-", cluster_df["px_row"].max())
        print("🖼️ img_width, height:", img_width, img_height)

        # Get expression values
        expr = expression_df[gene].values

        # Get spatial coordinates
        coords = cluster_df.rename(columns={"px_col": "x", "px_row": "y"})[["x", "y"]].copy()

        # Optional: dummy description (since you're not loading annotations)
        description = gene_descriptions.get(gene, "No description available.")

        hover_text = [f"Gene: {gene}<br>Expression: {v:.2f}<br>{description}" for v in expr]

        fig = go.Figure()
        fig.add_trace(go.Scattergl(
            x=coords["x"],
            y=coords["y"],
            mode="markers",
            marker=dict(
                size=6,
                color=expr,
                colorscale="inferno",
                showscale=True,
                colorbar=dict(title="Expression")
            ),
            text=hover_text,
            hoverinfo="text",
            name=gene
        ))

        fig.add_layout_image(
            dict(
                source=hires_img_base64,
                xref="x",
                yref="y",
                x=0,
                y=0,
                sizex=img_width,
                sizey=img_height,
                sizing="stretch",
                opacity=0.25,
                layer="below"
            )
        )

        fig.update_layout(
            title=f"Spatial Expression: {gene}",
            height=500,
            xaxis=dict(range=[0, img_width], showgrid=False),
            yaxis=dict(range=[img_height, 0], showgrid=False, scaleanchor="x", constrain="domain"),
            margin=dict(l=0, r=0, t=40, b=0)
        )

        return fig
