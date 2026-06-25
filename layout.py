"""Dash layout definition."""
from dash import dcc, html
from datetime import datetime
import dash_bootstrap_components as dbc

from styles import DROPDOWN_ROW_STYLE, DROPDOWN_STYLE, FOOTER_STYLE, HEADER_STYLE, LABEL_STYLE, SAMPLE_CONTROL_STYLE, CLUSTER_CONTROL_STYLE, SUBTITLE_STYLE, TITLE_STYLE

CURRENT_YEAR = datetime.now().year

def create_layout(sample_choices, sample_name_map):
    return html.Div([	 
    	 html.Div([
    	 html.Div([
            html.H3("Interactive Dashboard for Spatial Transcriptomics Analysis", style=TITLE_STYLE),
            html.P("Visualizing clusters, enriched biological pathways, and gene expression patterns in cancer spatial transcriptomics data.", style=SUBTITLE_STYLE),
        ]),
        ], style=HEADER_STYLE),
        # three horizontal partitions for plots, and information sections
        html.Div([
        # Left section – 45%
        html.Div([#left container opening
            html.H4("Spatial Expression of Enriched Pathways", style={'color': '#14274E'}),
            html.Div([
                html.Div([
                    html.Label("Select Sample:", style=LABEL_STYLE),
                    dcc.Store(id="loaded-sample-store"),
                    dcc.Store(id="loading-flag-store", data=False),
                    dcc.Dropdown(
                        id="sample-dropdown",
                        options=[{"label": sample_name_map[sample], "value": sample} for sample in sample_choices],
                        value=sample_choices[0],
                        disabled=False,
                        clearable=False,
                        placeholder="Select sample",
                        style=DROPDOWN_STYLE,
                    ),
                    dcc.Loading(
                        type="circle",
                        children=[html.Div(id="sample-output", style={"marginTop": "10px"})],
                    ),
                ], style=SAMPLE_CONTROL_STYLE),
                html.Div([
                    html.Label("Select Cluster:", style=LABEL_STYLE),
                    dcc.Dropdown(
                        id="cluster-dropdown",
                        options=[],
                        value=None,
                        placeholder="Select cluster",
                        disabled=True,
                        style=DROPDOWN_STYLE,
                    ),
                ], style=CLUSTER_CONTROL_STYLE),
            ], style=DROPDOWN_ROW_STYLE),
                #pathway dropdown container
                html.Div([
                html.Label("Select Pathways:", style={'font-weight': 'bold', 'margin-bottom': '5px', 'margin-top': '5px', 'margin-left': '10px', 'color': '#14274E'}),
                    dcc.Dropdown(
                    id="pathway-dropdown",
                    multi=True,
                    options=[],
                    placeholder="Select Pathway",
                    disabled=True
                    ),
                ], style={"width": "500px", "marginTop": "10px", "margin-left": "5px"}),# pathway dropdown
                #toggles container
                # Container for side-by-side toggles
                html.Div(style={'display': 'flex', 'justify-content': 'space-between', 'align-items': 'center', 'margin-top': '10px', 'gap': '20px'}, children=[
                    # significant pathways toggle    
    	            html.Div([
                        dcc.Checklist(
                            id="significance-toggle",
                            options=[{"label": " Show only significant pathways", "value": "significant"}],
                            value=["significant"],  # Default is checked
                            style={"flex": '1', 'marginLeft':'20px', 'color': '#14274E', 'font-size': '12px'}
                        ),

                   ]),
                # visualization mode toggles
                html.Div([
                    html.Label("Visualization Mode:", style={'color': '#14274E'}),
                        dcc.RadioItems(
                        id="vis-mode",
                        options=[
                            {"label": "Expression Heatmap", "value": "expression"},
                            {"label": "Pathway Blend", "value": "blend"}
                        ],
                        value="expression",
                        labelStyle={'display': 'inline-block', 'marginRight': '15px', 'marginLeft': '5px', 'color': '#14274E', 'font-size': '12px'}
                    ),
                    html.Div(id="blend-warning"),# > 1 pathway: select pathway blend mode
                 ], style={"flex": "1"})

            ]),# closing Side by side togles
            #Plot area
            html.Div(style={ "paddingRight": "20px"}, children=[
                dcc.Loading(
                    type="circle",
                    children=[dcc.Graph(id="spatial-overlay-plot")]
                )    
            ]),

            #below style for left overall container  
            ], style={
            'width': '45%',# sets the width of the container
            'backgroundColor': '#F1F6F9',
            'padding': '10px'
        }),#left container closing

        # Middle section – 30%
        html.Div([
            html.H4("Spatial Expression of Individual Genes", style={'color': '#14274E'}),
            #select gene dropdown
            html.Div(style={"width": "100%", "paddingLeft": "5px"}, children=[
                html.Div(id="pathway-warning"),# > 1 pathway: seeing genes of the first selected pathway
                html.Label("Select a gene from selected pathway:", style={'color': '#14274E', 'marginTop': '5px', 'marginBottom': '5px', 'marginTop': '10px'}),
                dcc.Dropdown(id="gene-dropdown", options=[], placeholder="Select gene", disabled=True),
                dcc.Graph(id="gene-expression-plot")
            ]),
        #middle section style
        ],style={
            'width': '30%', # sets container width
            'backgroundColor': '#d8e2e8',
            'padding': '10px'
        }),#middle section

        # Right section – 25%
        html.Div([
            html.H4("Dashboard Insights and Information", style={'color': '#14274E'}),
            #accordion for cluster plot
            html.Div([
                html.Label("Spots were grouped into clusters based on the similarity of their gene expression profiles, using the Leiden algorithm.", style={'font-weight': 'bold', 'margin-bottom': '20px', 'margin-top': '20px', 'margin-right': '10px', 'color': '#14274E'}),
                dbc.Accordion([# not closed
                    dbc.AccordionItem([#not closed
                       dcc.Graph(id="umap-plot", style={'height': '200px', 'width': '300px'})
                    ], title="Expand for plot of clusters")
                ], start_collapsed=True, style={'margin-top': '5px', 'margin-left': '5px'})       
            
            ]),
            # cluster overview accordion
            #dbc.Accordion([
            #    dbc.AccordionItem([
            #        html.Div(id="cluster-summary-text")
            #    ], title="Expand for Cluster and Pathway Overview")
            #], start_collapsed=True, style={'margin-top': '5px', 'margin-left': '5px'}),
        
            # selected cluster interpretation
            dbc.Accordion([# not closed
    			dbc.AccordionItem([# not closed
                    html.Div(id="cluster-interpretation-text"),
                    html.Div(id="distinct-pathways-summary"),
                ], title='cluster Interpretation')
            ], start_collapsed=True, style={"marginTop": "10px", "margin-left": "5px"}),
            # Data source accordion
            dbc.Accordion([
                dbc.AccordionItem([
                    html.Div(id="data-source"),
                    html.P([
    									"The spatial transcriptomics data used in this dashboard was obtained from from publicly available cancer datasets",
    									html.A("GEO database (GSE203612)", href="https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE203612", target="_blank"),
    									", this dashboard focused on breast cancer tissue samples profiled using the 10x Genomics Visium platform."
    								]),
    				html.P([
    									"The analysis and results of the enrire dataset are presented in the publication titled, ",
    									html.A("( Cancer cell states recur across tumor types and form specific interactions with the tumor microenvironment)"
    									, href="https://pubmed.ncbi.nlm.nih.gov/35931863/", target="_blank")
    								]),
                ], title="Data source and associated publication")
            ], start_collapsed=True, style={'margin-top': '5px', 'margin-left': '5px'}),
            # about dashboard
            dbc.Accordion([
                dbc.AccordionItem([
                    html.Div([
    					html.P("This dashboard was developed as a portfolio project to explore and visualize spatial transcriptomics data in the context of cancer biology."),
    					html.P("It allows users to interactively investigate tissue-resolved gene expression patterns, pathway enrichment across spatial clusters, and relationships between biological processes."),
    					html.P("Created by a data science and bioinformatics enthusiast with the goal of combining analytical rigor and intuitive visualization to support exploratory research in spatial genomics."),
    					html.P("The dashboard was built using Dash (Plotly), with preprocessing and analysis powered by Scanpy, GSEApy, and MyGene.info."),
    					html.P("Feel free to explore clusters, overlay enriched pathways, and examine the spatial expression of key genes involved in cancer progression."),
    					#html.P("For more information or collaboration inquiries, please get in touch.")
    				])

                ], title="About")
            ], start_collapsed=True, style={'margin-top': '5px', 'margin-left': '5px'}),
        
            # distinct pathways toggle
            html.Div([
                html.Label("Highlight Spatially Distinct Pathways"),
                    dcc.Checklist(
                        id="distinct-toggle",
                        options=[{"label": "Show Distinct Pathways", "value": "on"}],
                        value=['on']
                    )    
            ], style={'display': 'none'}),#'flex':'1', 'margin-right':'20px','color': '#ffffff'}),    
     
        #right section style
        ], style={
            'width': '25%',#sets width of container
            'backgroundColor': '#9BA4B4',
            'padding': '10px'
        }),
        #three partitions style
        ], style={
            'display': 'flex',
            'width': '100%',
            'gap': '0px'  # Optional: spacing between columns
        }),
        # info accordion
        html.Div(style={'width': '100%',  'padding-right': '10px', 'margin-left': '10px'}, children=[
        dbc.Accordion(
    				[
    				dbc.AccordionItem(
    				[
    					html.Div(style={'width': '100%', 'padding-right': '60px', 'margin-left': '0px', 'text-align': 'left'}, children=[
    					dbc.Accordion(
    					[
    						dbc.AccordionItem(
    							[
    								html.P("This dashboard was created as a portfolio project to demonstrate skills in spatial transcriptomics analysis, data visualization, and interactive dashboard development. It allows users to explore gene expression patterns, biological pathway enrichment, and clustering results in cancer tissue samples."),
        
    								html.P("The primary focus of this dashboard is to provide insights into how gene expression varies spatially across tumor sections, how distinct transcriptional clusters emerge, and which biological pathways are most enriched in different regions. Interactive visualizations such as UMAP plots, spatial expression overlays, and pathway/gene-specific exploration tools allow users to investigate complex spatial transcriptomics data intuitively."),
        
    								html.P("Key features of the dashboard include:"),
    								html.Ul([
    									html.Li("A UMAP projection for visualizing cluster separations based on transcriptional similarity."),
    									html.Li("Spatial expression overlays of biological pathways and individual genes across cancer tissue sections."),
    									html.Li("Dynamic exploration of top enriched pathways and gene lists within selected clusters."),
    									html.Li("Cluster-level summaries, including size, number of significant pathways, and biological highlights."),
    								]),

    								html.P("This project showcases the ability to integrate high-dimensional biological data, perform clustering and pathway enrichment analysis, and build an engaging, user-friendly dashboard to explore spatial patterns in complex cancer datasets."),
        
    								html.Hr(),

    								html.H5("Technology Used:"),
    								html.Ul([
    									html.Li("Dash & Plotly: For building the interactive web-based dashboard and data visualizations."),
    									html.Li("Scanpy: For spatial transcriptomics preprocessing, clustering, and enrichment analysis."),
    									html.Li("gseapy: For pathway enrichment based on gene expression data."),
    									html.Li("Pandas: For data manipulation, cleaning, and aggregation."),
    									html.Li("Python: General scripting, data handling, and analysis."),
    								]),
    							],
    							title="About this Dashboard"
    						),
						
    						dbc.AccordionItem(
    							[
    								html.P([
    									"The spatial transcriptomics data used in this dashboard was obtained from from publicly available cancer datasets",
    									html.A("GEO database (GSE203612)", href="https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE203612", target="_blank"),
    									", this dashboard focused on breast cancer tissue samples profiled using the 10x Genomics Visium platform."
    								]),
    								html.P([
    									"Each dataset includes gene expression matrices, spatial coordinates, tissue histology images, and associated metadata. ",
    									"The Visium platform captures gene expression at defined spots across tissue sections, allowing for the reconstruction of spatially resolved transcriptomic profiles. ",
    									"Gene-level expression, cluster assignments, and enrichment results were processed to enable interactive exploration through this dashboard."
    								]),
    							],
    							title="Where Data Was Obtained"
    						),
    						dbc.AccordionItem(
    							[
    								html.P("After downloading the spatial transcriptomics data, gene expression matrices were processed using the Scanpy library. "
    								"Normalization, dimensionality reduction (PCA), and neighborhood graph construction were performed to capture transcriptional relationships among spots."),
        
    								html.P("Spots were clustered using the Leiden community detection algorithm based on gene expression similarity. "
    								"Differential expression (DE) analysis was conducted between clusters using the Wilcoxon rank-sum test, "
    								"and p-values were adjusted for multiple testing using the Benjamini-Hochberg False Discovery Rate (FDR) correction."),
        
    								html.P([
    								"Pathway enrichment analysis was performed using gseapy and the MSigDB Hallmark 2020 gene sets. ",
    								html.A("The Hallmark gene sets", href="https://www.gsea-msigdb.org/gsea/msigdb/collections.jsp#H", target="_blank")," provide a curated collection of biologically meaningful gene programs, "
    								"offering a robust and non-redundant framework to interpret major biological processes active in cancer tissues."
    								]),
        
    								html.P("Gene spatial coordinates and histological images were integrated to enable overlaying gene or pathway expression on the tissue sections. "
    								"The dashboard was built using Dash and Plotly to allow dynamic exploration of clusters, pathways, and gene-level spatial patterns."),
    							],
    							title="How Data Was Processed"
    						),

    						dbc.AccordionItem(
    							[
    								html.P("Dashboard Layout: This dashboard offers a variety of interactive visualizations to explore spatial gene expression patterns, cluster structures, and biological pathway enrichment in cancer tissue samples:"),
        
    								html.Ul([
    									html.Li([
    										html.Strong("Sample Selection: "),
    										" Users can choose between available cancer tissue samples to explore spatial and transcriptional patterns across different datasets."
    									]),
            
    									html.Li([
    										html.Strong("UMAP Projection of Clusters: "),
    										" A UMAP plot visualizes the transcriptional similarity between spots, highlighting cluster separations based on gene expression profiles."
    									]),
            
    									html.Li([
    										html.Strong("Cluster Overview: "),
    										" An interactive summary showing the number of spots per cluster, number of significantly enriched pathways, and key biological processes active within each cluster."
    									]),
            
    									html.Li([
    										html.Strong("Spatial Expression of Pathways: "),
    										" Users can select biological pathways to visualize their spatial expression patterns across the tissue. Multiple pathways can be blended to observe overlap and separation."
    									]),
            
    									html.Li([
    										html.Strong("Spatial Expression of Individual Genes: "),
    										" Users can select genes from the top differentially expressed genes of a cluster to explore their spatial localization and contribution to biological pathways."
    									]),
    								]),
    							],
    							title="Dashboard Layout"
    						),
                    
    					],
    					start_collapsed=True
    				),
    		]),
    	],
    	title=html.Div("Expand for information about the dashboard", style={'width': '75%', 'display': 'flex', 'justify-content': 'left', 'text-align': 'center'}),
    	style={'border': '1px solid #000000','border-radius': '8px','text-align': 'center', 'margin-left': '0px', 'margin-right': '300px'},
    	),#top accordion
    	],
    	start_collapsed = True,
    	className="no-change-accordion"
    	),
    	]),


        # Footer with copyright
        html.Div(
            html.P(
                f"© {CURRENT_YEAR} Sophia Brauning. Built with Python, Dash and Plotly.",
                style=FOOTER_STYLE,
             ),
        ),
    ])# most outer container
