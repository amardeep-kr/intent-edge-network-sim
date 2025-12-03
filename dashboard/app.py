# # Placeholder for Dash + Cytoscape dashboard

# from dash import Dash, html, dcc, Input, Output, State, no_update
# import dash_cytoscape as cyto
# import json
# import requests

# # FastAPI backend URL
# BACKEND_URL = "http://127.0.0.1:8000"

# app = Dash(__name__, title="Intent Edge Network Dashboard")



# def build_topology_elements_from_config(config: dict) -> list[dict]:
#     """
#     Build Cytoscape elements (nodes + edges) from a ScenarioConfig dict.

#     Simple model:
#       - sensors: sensor-0 .. sensor-(N-1)
#       - edges:   edge-0 .. edge-(E-1)
#       - cloud:   cloud-0
#       - connections: sensors -> edges (round-robin), edges -> cloud
#     """
#     nodes_cfg = config.get("nodes", {}) if config else {}
#     sensors = int(nodes_cfg.get("sensors", 0) or 0)
#     edges = int(nodes_cfg.get("edges", 0) or 0)
#     cloud_count = int(nodes_cfg.get("cloud", 1) or 1)

#     elements: list[dict] = []

#     # --- create nodes ---

#     # Cloud node(s)
#     for i in range(cloud_count):
#         cid = f"cloud-{i}"
#         elements.append(
#             {
#                 "data": {"id": cid, "label": f"Cloud {i}"},
#                 "classes": "cloud",
#             }
#         )

#     # Edge nodes (at least one for visualization)
#     edge_count = max(edges, 1)
#     for i in range(edge_count):
#         eid = f"edge-{i}"
#         elements.append(
#             {
#                 "data": {"id": eid, "label": f"Edge {i}"},
#                 "classes": "edge",
#             }
#         )

#     # Sensor nodes
#     for i in range(sensors):
#         sid = f"sensor-{i}"
#         elements.append(
#             {
#                 "data": {"id": sid, "label": f"S{i}"},
#                 "classes": "sensor",
#             }
#         )

#     # --- now compute ids from *nodes only* ---

#     node_elements = [el for el in elements if "id" in el.get("data", {})]

#     edge_ids = [
#         el["data"]["id"]
#         for el in node_elements
#         if str(el["data"]["id"]).startswith("edge-")
#     ]
#     if not edge_ids:
#         edge_ids = ["edge-0"]

#     cloud_ids = [
#         el["data"]["id"]
#         for el in node_elements
#         if str(el["data"]["id"]).startswith("cloud-")
#     ]
#     target_cloud = cloud_ids[0] if cloud_ids else None

#     # --- create edges ---

#     # Sensors -> edges (round-robin)
#     for i in range(sensors):
#         sid = f"sensor-{i}"
#         eid = edge_ids[i % len(edge_ids)]
#         elements.append(
#             {
#                 "data": {
#                     "source": sid,
#                     "target": eid,
#                 }
#             }
#         )

#     # Edges -> cloud
#     if target_cloud is not None:
#         for eid in edge_ids:
#             elements.append(
#                 {
#                     "data": {
#                         "source": eid,
#                         "target": target_cloud,
#                     }
#                 }
#             )

#     return elements


# app.layout = html.Div(
#     style={"display": "flex", "flexDirection": "column", "gap": "1rem", "padding": "1rem"},
#     children=[
#         html.H2("Intent Edge Network Dashboard"),
#         html.Div(
#             style={"display": "flex", "gap": "1rem"},
#             children=[
#                 html.Div(
#                     style={"flex": "1"},
#                     children=[
#                         html.Label("Intent text:"),
#                         dcc.Textarea(
#                             id="intent-input",
#                             style={"width": "100%", "height": "120px"},
#                             value=(
#                                 "Create two edge sites with 15 sensors per site, "
#                                 "weak inter-site link, use MQTT-style publish-subscribe "
#                                 "and prioritize reliability for 5 minutes."
#                             ),
#                         ),
#                         html.Br(),
#                         html.Button("Parse intent", id="parse-button", n_clicks=0),
#                         html.Div(id="intent-error", style={"color": "red", "marginTop": "0.5rem"}),
#                     ],
#                 ),
#                 html.Div(
#                     style={"flex": "1"},
#                     children=[
#                         html.H4("Parsed Scenario Configuration"),
#                         html.Pre(
#                             id="config-output",
#                             style={
#                                 "backgroundColor": "#111",
#                                 "color": "#eee",
#                                 "padding": "0.5rem",
#                                 "height": "200px",
#                                 "overflowY": "auto",
#                                 "fontSize": "0.8rem",
#                             },
#                         ),
#                     ],
#                 ),
#             ],
#         ),
#         html.Div(
#             style={"height": "400px", "border": "1px solid #444"},
#             children=[
#                 cyto.Cytoscape(
#                 # dash_cytoscape.Cytoscape(
#                     id="topology-graph",
#                     layout={"name": "breadthfirst"},
#                     style={"width": "100%", "height": "100%"},
#                     elements=[],
#                     stylesheet=[
#                         {
#                             "selector": ".sensor",
#                             "style": {
#                                 "background-color": "#1f77b4",
#                                 "label": "data(label)",
#                                 "shape": "ellipse",
#                             },
#                         },
#                         {
#                             "selector": ".edge",
#                             "style": {
#                                 "background-color": "#ff7f0e",
#                                 "label": "data(label)",
#                                 "shape": "round-rectangle",
#                             },
#                         },
#                         {
#                             "selector": ".cloud",
#                             "style": {
#                                 "background-color": "#2ca02c",
#                                 "label": "data(label)",
#                                 "shape": "diamond",
#                             },
#                         },
#                         {
#                             "selector": "edge",
#                             "style": {
#                                 "line-color": "#aaa",
#                                 "curve-style": "bezier",
#                                 "target-arrow-shape": "triangle",
#                                 "target-arrow-color": "#aaa",
#                             },
#                         },
#                     ],
#                 )
#             ],
#         ),
#         dcc.Store(id="scenario-store"),
#     ],
# )


# # @app.callback(
# #     outputs=[
# #         Output("config-output", "children"),
# #         Output("topology-graph", "elements"),
# #         Output("intent-error", "children"),
# #         Output("scenario-store", "data"),
# #     ],
# #     inputs=[Input("parse-button", "n_clicks")],
# #     state=[State("intent-input", "value"), State("scenario-store", "data")],
# # )
# # def on_parse_intent(n_clicks, intent_text, prev_data):
# #     if not n_clicks:
# #         # nothing clicked yet
# #         return "", [], "", prev_data

# #     if not intent_text or not intent_text.strip():
# #         return "", [], "Intent text is empty.", prev_data

# #     try:
# #         resp = requests.post(
# #             f"{BACKEND_URL}/intent",
# #             json={"text": intent_text},
# #             timeout=5,
# #         )
# #     except Exception as exc:
# #         return "", [], f"Error contacting backend: {exc}", prev_data

# #     if resp.status_code != 200:
# #         return "", [], f"Backend returned status {resp.status_code}", prev_data

# #     try:
# #         config = resp.json()
# #     except Exception as exc:
# #         return "", [], f"Failed to decode backend response: {exc}", prev_data

# #     pretty = json.dumps(config, indent=2)
# #     elements = build_topology_elements_from_config(config)

# #     return pretty, elements, "", config

# @app.callback(
#     Output("config-output", "children"),
#     Output("topology-graph", "elements"),
#     Output("intent-error", "children"),
#     Output("scenario-store", "data"),
#     Input("parse-button", "n_clicks"),
#     State("intent-input", "value"),
#     State("scenario-store", "data"),
# )
# def on_parse_intent(n_clicks, intent_text, prev_data):
#     if not n_clicks:
#         # nothing clicked yet
#         return "", [], "", prev_data

#     if not intent_text or not intent_text.strip():
#         return "", [], "Intent text is empty.", prev_data

#     try:
#         resp = requests.post(
#             f"{BACKEND_URL}/intent",
#             json={"text": intent_text},
#             timeout=5,
#         )
#     except Exception as exc:
#         return "", [], f"Error contacting backend: {exc}", prev_data

#     if resp.status_code != 200:
#         return "", [], f"Backend returned status {resp.status_code}", prev_data

#     try:
#         config = resp.json()
#     except Exception as exc:
#         return "", [], f"Failed to decode backend response: {exc}", prev_data

#     pretty = json.dumps(config, indent=2)
#     elements = build_topology_elements_from_config(config)

#     return pretty, elements, "", config

# # if __name__ == "__main__":
# #     app.run_server(host="127.0.0.1", port=8050, debug=True)

# if __name__ == "__main__":
#     app.run(host="127.0.0.1", port=8050, debug=True)







from dash import Dash, html, dcc, Input, Output, State
import dash_cytoscape as cyto
import json
import requests
import plotly.graph_objects as go

# FastAPI backend URL
BACKEND_URL = "http://127.0.0.1:8000"

app = Dash(__name__, title="Intent Edge Network Dashboard")


def build_topology_elements_from_config(config: dict) -> list[dict]:
    """
    Build Cytoscape elements (nodes + edges) from a ScenarioConfig dict.

    Simple model:
      - sensors: sensor-0 .. sensor-(N-1)
      - edges:   edge-0 .. edge-(E-1)
      - cloud:   cloud-0
      - connections: sensors -> edges (round-robin), edges -> cloud
    """
    nodes_cfg = config.get("nodes", {}) if config else {}
    sensors = int(nodes_cfg.get("sensors", 0) or 0)
    edges = int(nodes_cfg.get("edges", 0) or 0)
    cloud_count = int(nodes_cfg.get("cloud", 1) or 1)

    elements: list[dict] = []

    # --- create nodes ---

    # Cloud node(s)
    for i in range(cloud_count):
        cid = f"cloud-{i}"
        elements.append(
            {
                "data": {"id": cid, "label": f"Cloud {i}"},
                "classes": "cloud",
            }
        )

    # Edge nodes (at least one for visualization)
    edge_count = max(edges, 1)
    for i in range(edge_count):
        eid = f"edge-{i}"
        elements.append(
            {
                "data": {"id": eid, "label": f"Edge {i}"},
                "classes": "edge",
            }
        )

    # Sensor nodes
    for i in range(sensors):
        sid = f"sensor-{i}"
        elements.append(
            {
                "data": {"id": sid, "label": f"S{i}"},
                "classes": "sensor",
            }
        )

    # --- now compute ids from *nodes only* ---

    node_elements = [el for el in elements if "id" in el.get("data", {})]

    edge_ids = [
        el["data"]["id"]
        for el in node_elements
        if str(el["data"]["id"]).startswith("edge-")
    ]
    if not edge_ids:
        edge_ids = ["edge-0"]

    cloud_ids = [
        el["data"]["id"]
        for el in node_elements
        if str(el["data"]["id"]).startswith("cloud-")
    ]
    target_cloud = cloud_ids[0] if cloud_ids else None

    # --- create edges ---

    # Sensors -> edges (round-robin)
    for i in range(sensors):
        sid = f"sensor-{i}"
        eid = edge_ids[i % len(edge_ids)]
        elements.append(
            {
                "data": {
                    "source": sid,
                    "target": eid,
                }
            }
        )

    # Edges -> cloud
    if target_cloud is not None:
        for eid in edge_ids:
            elements.append(
                {
                    "data": {
                        "source": eid,
                        "target": target_cloud,
                    }
                }
            )

    return elements


def compute_metrics_from_config(config: dict) -> dict:
    """
    Derive simple, interview-friendly metrics from ScenarioConfig.

    This is not a real network model, just a plausible heuristic:
      - latency depends on link quality and load
      - reliability depends on objective and link quality
      - bandwidth depends on number of sensors and duration
    """
    if not config:
        return {
            "sensor_count": 0,
            "edge_count": 0,
            "duration_s": 0,
            "avg_latency_ms": 0.0,
            "reliability_pct": 0.0,
            "bandwidth_kbps": 0.0,
        }

    nodes = config.get("nodes", {})
    links = config.get("links", {})
    sim = config.get("simulation", {})
    objective = config.get("objective", "balanced")

    sensor_count = int(nodes.get("sensors", 0) or 0)
    edge_count = int(nodes.get("edges", 0) or 0)
    duration_s = int(sim.get("duration_s", 120) or 120)
    link_quality = links.get("inter_site_quality", "normal")

    # Base latency per flow
    base_latency = 40.0  # ms

    if link_quality == "weak":
        base_latency += 40.0
    elif link_quality == "strong":
        base_latency -= 15.0

    # More sensors → more contention → more latency
    if sensor_count > 0:
        base_latency += min(sensor_count * 0.8, 40.0)

    # Latency objective nudges it slightly down (pretend orchestrator optimizes)
    if "latency" in objective:
        base_latency -= 10.0

    avg_latency_ms = max(base_latency, 5.0)

    # Reliability between 85 and 99 %
    reliability = 92.0
    if link_quality == "weak":
        reliability -= 5.0
    elif link_quality == "strong":
        reliability += 3.0

    if "reliab" in objective or "resilien" in objective:
        reliability += 4.0

    reliability_pct = max(min(reliability, 99.0), 80.0)

    # Bandwidth usage: each sensor sends a small flow
    bandwidth_per_sensor = 4.0  # kbps, pretend
    bandwidth_kbps = sensor_count * bandwidth_per_sensor

    return {
        "sensor_count": sensor_count,
        "edge_count": edge_count,
        "duration_s": duration_s,
        "avg_latency_ms": round(avg_latency_ms, 1),
        "reliability_pct": round(reliability_pct, 1),
        "bandwidth_kbps": round(bandwidth_kbps, 1),
    }


def empty_metrics_figure() -> go.Figure:
    fig = go.Figure()
    fig.update_layout(
        template="plotly_white",
        title="Scenario Metrics",
        xaxis_title="Metric",
        yaxis_title="Value",
    )
    return fig


def metrics_figure_from_stats(stats: dict) -> go.Figure:
    fig = go.Figure()

    x = ["Latency (ms)", "Reliability (%)", "Bandwidth (kbps)"]
    y = [
        stats.get("avg_latency_ms", 0.0),
        stats.get("reliability_pct", 0.0),
        stats.get("bandwidth_kbps", 0.0),
    ]

    fig.add_bar(x=x, y=y)

    subtitle = (
        f"Sensors: {stats.get('sensor_count', 0)}, "
        f"Edges: {stats.get('edge_count', 0)}, "
        f"Duration: {stats.get('duration_s', 0)} s"
    )

    fig.update_layout(
        template="plotly_white",
        title=f"Scenario Metrics ({subtitle})",
        xaxis_title="Metric",
        yaxis_title="Value",
    )
    return fig


app.layout = html.Div(
    style={"display": "flex", "flexDirection": "column", "gap": "1rem", "padding": "1rem"},
    children=[
        html.H2("Intent Edge Network Dashboard"),
        html.Div(
            style={"display": "flex", "gap": "1rem"},
            children=[
                html.Div(
                    style={"flex": "1"},
                    children=[
                        html.Label("Intent text:"),
                        dcc.Textarea(
                            id="intent-input",
                            style={"width": "100%", "height": "120px"},
                            value=(
                                "Deploy an industrial IoT testbed with 3 sites, each site connected "
    "through an edge router and access switch, hosting 15 sensors per site. "
    "Assume weak inter-site WAN links, use MQTT-style publish-subscribe "
    "for telemetry, and prioritize reliability over latency for a 5-minute run."
                            ),
                        ),
                        html.Br(),
                        html.Button("Parse intent", id="parse-button", n_clicks=0),
                        html.Div(id="intent-error", style={"color": "red", "marginTop": "0.5rem"}),
                    ],
                ),
                html.Div(
                    style={"flex": "1"},
                    children=[
                        html.H4("Parsed Scenario Configuration"),
                        html.Pre(
                            id="config-output",
                            style={
                                "backgroundColor": "#111",
                                "color": "#eee",
                                "padding": "0.5rem",
                                "height": "200px",
                                "overflowY": "auto",
                                "fontSize": "0.8rem",
                            },
                        ),
                    ],
                ),
            ],
        ),
        html.Div(
            style={"height": "400px", "border": "1px solid #444"},
            children=[
                cyto.Cytoscape(
                    id="topology-graph",
                    layout={"name": "breadthfirst"},
                    style={"width": "100%", "height": "100%"},
                    elements=[],
                    stylesheet=[
                        {
                            "selector": ".sensor",
                            "style": {
                                "background-color": "#1f77b4",
                                "label": "data(label)",
                                "shape": "ellipse",
                            },
                        },
                        {
                            "selector": ".edge",
                            "style": {
                                "background-color": "#ff7f0e",
                                "label": "data(label)",
                                "shape": "round-rectangle",
                            },
                        },
                        {
                            "selector": ".cloud",
                            "style": {
                                "background-color": "#2ca02c",
                                "label": "data(label)",
                                "shape": "diamond",
                            },
                        },
                        {
                            "selector": "edge",
                            "style": {
                                "line-color": "#aaa",
                                "curve-style": "bezier",
                                "target-arrow-shape": "triangle",
                                "target-arrow-color": "#aaa",
                            },
                        },
                    ],
                )
            ],
        ),
        html.Div(
            style={"marginTop": "1rem"},
            children=[
                html.H4("Scenario Metrics"),
                dcc.Graph(id="metrics-graph", figure=empty_metrics_figure()),
            ],
        ),
        dcc.Store(id="scenario-store"),
    ],
)


@app.callback(
    Output("config-output", "children"),
    Output("topology-graph", "elements"),
    Output("intent-error", "children"),
    Output("scenario-store", "data"),
    Output("metrics-graph", "figure"),
    Input("parse-button", "n_clicks"),
    State("intent-input", "value"),
    State("scenario-store", "data"),
)
def on_parse_intent(n_clicks, intent_text, prev_data):
    if not n_clicks:
        # nothing clicked yet
        return "", [], "", prev_data, empty_metrics_figure()

    if not intent_text or not intent_text.strip():
        return "", [], "Intent text is empty.", prev_data, empty_metrics_figure()

    try:
        resp = requests.post(
            f"{BACKEND_URL}/intent",
            json={"text": intent_text},
            timeout=5,
        )
    except Exception as exc:
        return "", [], f"Error contacting backend: {exc}", prev_data, empty_metrics_figure()

    if resp.status_code != 200:
        return "", [], f"Backend returned status {resp.status_code}", prev_data, empty_metrics_figure()

    try:
        config = resp.json()
    except Exception as exc:
        return "", [], f"Failed to decode backend response: {exc}", prev_data, empty_metrics_figure()

    pretty = json.dumps(config, indent=2)
    elements = build_topology_elements_from_config(config)

    stats = compute_metrics_from_config(config)
    fig = metrics_figure_from_stats(stats)

    return pretty, elements, "", config, fig


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8050, debug=True)
