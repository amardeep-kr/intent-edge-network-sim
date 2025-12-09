



from dash import Dash, html, dcc, Input, Output, State
import dash_cytoscape as cyto
import json
import requests
import plotly.graph_objects as go
import time  # NEW: for simple timing


# -------------------------------------------------------
# BACKEND URL
# -------------------------------------------------------
BACKEND_URL = "http://127.0.0.1:8000"


# -------------------------------------------------------
# TOPOLOGY + METRICS HELPERS
# -------------------------------------------------------

def build_topology_elements_from_config(config: dict) -> list[dict]:
    if not config:
        return []

    nodes_cfg = config.get("nodes", {}) or {}
    links_cfg = config.get("links", {}) or {}

    sensors = int(nodes_cfg.get("sensors", 0) or 0)
    edges = int(nodes_cfg.get("edges", 0) or 0)
    cloud_count = int(nodes_cfg.get("cloud", 1) or 1)

    link_quality = links_cfg.get("inter_site_quality", "normal")

    # color for link quality
    if link_quality == "weak":
        edge_color = "#ef4444"     # red
    elif link_quality == "strong":
        edge_color = "#22c55e"     # green
    else:
        edge_color = "#6b7280"     # gray

    elements = []

    # cloud nodes
    for i in range(max(cloud_count, 1)):
        cid = f"cloud-{i}"
        elements.append({
            "data": {"id": cid, "label": f"Cloud {i}", "role": "cloud"},
            "classes": "cloud"
        })

    # edge nodes
    edge_count = max(edges, 1)
    for i in range(edge_count):
        eid = f"edge-{i}"
        elements.append({
            "data": {"id": eid, "label": f"Edge {i}", "role": "edge"},
            "classes": "edge"
        })

    # sensors
    for i in range(sensors):
        sid = f"sensor-{i}"
        elements.append({
            "data": {"id": sid, "label": f"S{i}", "role": "sensor"},
            "classes": "sensor"
        })

    edge_ids = [f"edge-{i}" for i in range(edge_count)]
    cloud_id = "cloud-0"

    # sensor → edge
    for i in range(sensors):
        sid = f"sensor-{i}"
        eid = edge_ids[i % len(edge_ids)]
        elements.append({
            "data": {
                "source": sid, "target": eid, "color": edge_color
            }
        })

    # edge → cloud
    for eid in edge_ids:
        elements.append({
            "data": {
                "source": eid, "target": cloud_id, "color": edge_color
            }
        })

    return elements


def compute_metrics_from_config(config: dict) -> dict:
    if not config:
        return {
            "sensor_count": 0,
            "edge_count": 0,
            "duration_s": 0,
            "avg_latency_ms": 0.0,
            "reliability_pct": 0.0,
            "bandwidth_kbps": 0.0,
        }

    nodes = config.get("nodes", {}) or {}
    links = config.get("links", {}) or {}
    sim = config.get("simulation", {}) or {}
    objective = (config.get("objective") or "balanced").lower()

    sensor_count = int(nodes.get("sensors", 0) or 0)
    edge_count = int(nodes.get("edges", 0) or 0)
    duration_s = int(sim.get("duration_s", 120) or 120)
    link_quality = links.get("inter_site_quality", "normal")

    base_latency = 40

    if link_quality == "weak":
        base_latency += 40
    elif link_quality == "strong":
        base_latency -= 15

    base_latency += min(sensor_count * 0.8, 40)

    if "latency" in objective:
        base_latency -= 10

    avg_latency_ms = max(base_latency, 5)

    reliability = 92
    if link_quality == "weak":
        reliability -= 5
    elif link_quality == "strong":
        reliability += 3

    if "reliab" in objective:
        reliability += 4

    reliability = max(min(reliability, 99), 80)

    bandwidth_kbps = sensor_count * 4

    return {
        "sensor_count": sensor_count,
        "edge_count": edge_count,
        "duration_s": duration_s,
        "avg_latency_ms": round(avg_latency_ms, 1),
        "reliability_pct": round(reliability, 1),
        "bandwidth_kbps": round(bandwidth_kbps, 1),
    }


def empty_metrics_figure():
    fig = go.Figure()
    fig.update_layout(
        template="plotly_white",
        title="Scenario Metrics (awaiting intent)"
    )
    return fig


def metrics_figure_from_stats(stats):
    fig = go.Figure()
    x = ["Latency (ms)", "Reliability (%)", "Bandwidth (kbps)"]
    y = [
        stats["avg_latency_ms"],
        stats["reliability_pct"],
        stats["bandwidth_kbps"]
    ]

    fig.add_bar(x=x, y=y, marker_color=["#3b82f6", "#10b981", "#f59e0b"])

    fig.update_layout(
        template="plotly_white",
        title="Scenario Metrics",
        xaxis_title="Metric",
        yaxis_title="Value",
        height=320
    )
    return fig


# -------------------------------------------------------
# DASH APP UI
# -------------------------------------------------------

app = Dash(__name__, title="Intent Edge Network Dashboard")


app.layout = html.Div(
    style={
        "minHeight": "100vh",
        "backgroundColor": "#eef2ff",
        "padding": "1.5rem",
        "fontFamily": "Segoe UI, sans-serif",
    },
    children=[

        # title
        html.H2(
            "Intent Edge Network Dashboard",
            style={"marginBottom": "0.5rem", "color": "#1e3a8a"},
        ),

        # ---------------------------------------------------
        # WORKFLOW PANEL (with run info)
        # ---------------------------------------------------

                            html.Div(
                        id="workflow-panel",
                        style={
                            "background": "#ffffff",
                            "borderRadius": "0.5rem",
                            "padding": "0.75rem",
                            "marginBottom": "1rem",
                            "boxShadow": "0 1px 3px rgba(0,0,0,0.08)",

                            # keep height stable
                            "minHeight": "130px",          # tweak 120–150px if you want
                            "display": "flex",
                            "flexDirection": "column",
                            "justifyContent": "center",
                        },
                        children=[
                            html.Div(
                                "Workflow Execution",
                                style={"fontWeight": "600", "marginBottom": "0.25rem"},
                            ),
                            html.Div(
                                id="workflow-run-info",
                                style={
                                    "fontSize": "0.8rem",
                                    "color": "#4b5563",
                                    "marginBottom": "0.35rem",
                                },
                                children="Waiting for first run…",
                            ),
                            html.Ul(
                                id="workflow-steps",
                                style={"fontSize": "0.85rem", "color": "#1f2937", "margin": 0},
                            ),
                        ],
                    ),




        # ---------------------------------------------------
        # TOP ROW (Intent + Config)
        # ---------------------------------------------------
        html.Div(
            style={"display": "flex", "gap": "1rem", "marginBottom": "1rem"},
            children=[
                # Intent input
                html.Div(
                    style={
                        "flex": "1",
                        "backgroundColor": "#ffffff",
                        "borderRadius": "0.5rem",
                        "padding": "0.75rem",
                        "boxShadow": "0 1px 3px rgba(0,0,0,0.08)",
                    },
                    children=[
                        html.Div("Intent Text", style={"fontWeight": "600"}),
                        dcc.Textarea(
                            id="intent-input",
                            value=(
                                "Deploy 3 industrial sites with 20 sensors per site, "
                                "weak inter-site links, use MQTT-style publish-subscribe "
                                "and prioritize reliability for a 5-minute run."
                            ),
                            style={
                                "width": "95%",
                                "height": "140px",
                                "borderRadius": "0.375rem",
                                "border": "1px solid #cbd5e1",
                                "padding": "0.5rem",
                            },
                        ),
                        html.Button(
                            "Parse Intent",
                            id="parse-button",
                            n_clicks=0,
                            style={
                                "marginTop": "0.5rem",
                                "padding": "0.4rem 0.9rem",
                                "borderRadius": "0.375rem",
                                "border": "none",
                                "background": "#3b82f6",
                                "color": "white",
                                "cursor": "pointer",
                            },
                        ),
                        html.Div(id="intent-error", style={"color": "#b91c1c"}),
                    ],
                ),

                # Parsed config
                html.Div(
                    style={
                        "flex": "1",
                        "backgroundColor": "#ffffff",
                        "borderRadius": "0.5rem",
                        "padding": "0.75rem",
                        "boxShadow": "0 1px 3px rgba(0,0,0,0.08)",
                    },
                    children=[
                        html.Div("Parsed Scenario Config", style={"fontWeight": "600"}),
                        dcc.Loading(
                            id="config-loading",
                            type="circle",
                            children=html.Pre(
                                id="config-output",
                                style={
                                    "background": "#0f172a",
                                    "color": "#f1f5f9",
                                    "padding": "0.5rem",
                                    "height": "240px",
                                    "overflowY": "auto",
                                    "borderRadius": "0.4rem",
                                    "fontSize": "0.85rem",

                                    # important bits:
                                    "whiteSpace": "pre-wrap",   # allow wrapping
                                    "wordBreak": "break-word",  # break long words/strings
                                },
                            ),
                        ),

                        html.Button(
                            "Copy JSON",
                            id="copy-json-btn",
                            n_clicks=0,
                            style={
                                "marginTop": "0.4rem",
                                "padding": "0.3rem 0.7rem",
                                "borderRadius": "0.375rem",
                                "background": "white",
                                "border": "1px solid #94a3b8",
                                "cursor": "pointer",
                            },
                        ),
                        html.Div(id="copy-json-status", style={"fontSize": "0.8rem"}),
                    ],
                ),
            ],
        ),

        # ---------------------------------------------------
        # MIDDLE (Topology + Node Details)
        # ---------------------------------------------------
        html.Div(
            style={"display": "flex", "gap": "1rem", "marginBottom": "1rem"},
            children=[
                # topology
                html.Div(
                    style={
                        "flex": "2",
                        "background": "#ffffff",
                        "borderRadius": "0.5rem",
                        "padding": "0.75rem",
                        "boxShadow": "0 1px 3px rgba(0,0,0,0.08)",
                    },
                    children=[
                        html.Div("Network Topology", style={"fontWeight": "600"}),
                        dcc.Loading(        # spinner for topology
                            id="topology-loading",
                            type="circle",
                            children=cyto.Cytoscape(
                                id="topology-graph",
                                style={"width": "100%", "height": "330px"},
                                layout={
                                    "name": "breadthfirst",
                                    "directed": True,
                                    "spacingFactor": 1.25,
                                    "animate": True,
                                    "animationDuration": 600,
                                },
                                elements=[],
                                stylesheet=[
                                    {"selector": ".sensor",
                                     "style": {"background-color": "#3b82f6", "label": "data(label)"}},
                                    {"selector": ".edge",
                                     "style": {
                                         "background-color": "#f97316",
                                         "label": "data(label)",
                                         "border-width": 2,
                                         "border-color": "#1e293b",
                                     }},
                                    {"selector": ".cloud",
                                     "style": {"background-color": "#10b981", "label": "data(label)"}},
                                    {"selector": "edge",
                                     "style": {
                                         "line-color": "data(color)",
                                         "target-arrow-color": "data(color)",
                                         "target-arrow-shape": "triangle",
                                         "curve-style": "bezier",
                                     }},
                                ],
                            ),
                        ),
                    ],
                ),

                # node details
                html.Div(
                    style={
                        "flex": "1",
                        "background": "#ffffff",
                        "borderRadius": "0.5rem",
                        "padding": "0.75rem",
                        "boxShadow": "0 1px 3px rgba(0,0,0,0.08)",
                    },
                    children=[
                        html.Div("Node Details", style={"fontWeight": "600"}),
                        html.Div(id="node-details", style={"fontSize": "0.85rem"})
                    ],
                ),
            ],
        ),

        # ---------------------------------------------------
        # METRICS
        # ---------------------------------------------------
        html.Div(
            style={
                "background": "#ffffff",
                "borderRadius": "0.5rem",
                "padding": "0.75rem",
                "boxShadow": "0 1px 3px rgba(0,0,0,0.08)",
            },
            children=[
                html.Div("Scenario Metrics", style={"fontWeight": "600"}),
                dcc.Loading(     # spinner for metrics
                    id="metrics-loading",
                    type="circle",
                    children=dcc.Graph(id="metrics-graph", figure=empty_metrics_figure()),
                ),
            ],
        ),

        dcc.Store(id="scenario-store"),
    ],
)

# -------------------------------------------------------
# CALLBACKS
# -------------------------------------------------------

@app.callback(
    Output("config-output", "children"),
    Output("topology-graph", "elements"),
    Output("intent-error", "children"),
    Output("scenario-store", "data"),
    Output("metrics-graph", "figure"),
    Output("workflow-steps", "children"),
    Output("workflow-run-info", "children"),   # NEW
    Input("parse-button", "n_clicks"),
    State("intent-input", "value"),
    State("scenario-store", "data"),
)
def parse_intent(n, text, prev_data):
    if not n:
        return (
            "",
            [],
            "",
            prev_data,
            empty_metrics_figure(),
            [
                html.Li("1. Waiting for input…"),
                html.Li("2. Parser idle"),
                html.Li("3. ScenarioConfig not generated"),
                html.Li("4. Topology empty"),
            ],
            "Waiting for first run…",
        )

    start = time.perf_counter()

    # Step skeleton (not actually shown intermediate, just conceptual)
    steps = [
        html.Li("✓ Intent received", style={"color": "#2563eb"}),
        html.Li("Parsing intent…", style={"color": "#334155"}),
    ]

    if not text.strip():
        run_info = "Last run failed: empty input."
        return (
            "",
            [],
            "Empty input.",
            prev_data,
            empty_metrics_figure(),
            steps + [html.Li("Error: No text provided", style={"color": "#dc2626"})],
            run_info,
        )

    try:
        resp = requests.post(
            f"{BACKEND_URL}/intent",
            json={"text": text},
            timeout=5,
        )
    except Exception as e:
        run_info = "Last run failed: backend unreachable."
        return (
            "",
            [],
            str(e),
            prev_data,
            empty_metrics_figure(),
            steps + [html.Li("Error: Backend not reachable", style={"color": "#dc2626"})],
            run_info,
        )

    if resp.status_code != 200:
        run_info = f"Last run failed: HTTP {resp.status_code}."
        return (
            "",
            [],
            "Backend error",
            prev_data,
            empty_metrics_figure(),
            steps + [html.Li("Error: Backend failed", style={"color": "#dc2626"})],
            run_info,
        )

    config = resp.json()

    pretty = json.dumps(config, indent=2)
    elements = build_topology_elements_from_config(config)
    stats = compute_metrics_from_config(config)
    fig = metrics_figure_from_stats(stats)

    end = time.perf_counter()
    duration_ms = int((end - start) * 1000)

    run_info = (
        f"Run time: {duration_ms} ms • "
        f"Sensors: {stats['sensor_count']} • "
        f"Edges: {stats['edge_count']} • "
        f"Duration: {stats['duration_s']} s"
    )

    step_items = [
        html.Li("✓ Intent received", style={"color": "#2563eb"}),
        html.Li("✓ Parsed into ScenarioConfig", style={"color": "#16a34a"}),
        html.Li("✓ Topology generated", style={"color": "#10b981"}),
        html.Li("✓ Metrics computed", style={"color": "#10b981"}),
    ]

    return pretty, elements, "", config, fig, step_items, run_info


@app.callback(
    Output("node-details", "children"),
    Input("topology-graph", "tapNodeData"),
    State("scenario-store", "data"),
)
def node_clicked(node_data, scenario):
    if node_data is None:
        return "Click a node to see details."

    nid = node_data["id"]
    role = node_data.get("role", "")
    label = node_data.get("label", "")

    detail_list = [
        f"ID: {nid}",
        f"Label: {label}",
        f"Role: {role}",
    ]

    if scenario:
        detail_list.append(f"Protocol: {scenario.get('protocol')}")
        detail_list.append(f"Objective: {scenario.get('objective')}")

    return html.Ul([html.Li(i) for i in detail_list])


# copy JSON button
app.clientside_callback(
    """
    function(n, text) {
        if (!n) return "";
        navigator.clipboard.writeText(text || "");
        return "JSON copied!";
    }
    """,
    Output("copy-json-status", "children"),
    Input("copy-json-btn", "n_clicks"),
    State("config-output", "children"),
)


# -------------------------------------------------------
# RUN
# -------------------------------------------------------
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8050, debug=True)
