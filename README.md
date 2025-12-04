# Intent-Edge Network Simulator (Prototype)

This project is a **prototype intent-driven edge network orchestrator and visualizer**.

It demonstrates an end-to-end pipeline:

1. **Natural language intent**  
   A user describes an edge/IoT deployment in free text, e.g.:

   > “Deploy 3 sites with 20 sensors per site, weak inter-site links, use MQTT publish–subscribe and prioritize reliability for 5 minutes.”

2. **Intent parsing (FastAPI backend)**  
   A **rule-based parser** converts the text into a normalized `ScenarioConfig`:

   - number of sites, sensors, edge nodes, cloud nodes  
   - link quality (weak / normal / strong)  
   - objective (reliability / latency / bandwidth / balanced)  
   - protocol hint (mqtt-like / tcp-like / udp-like / auto)  
   - simulation duration (seconds)

3. **Scenario visualization (Dash + Cytoscape)**  
   A dashboard connects to the backend and shows:

   - a **topology graph** (sensors → edge nodes → cloud)  
   - a **parsed configuration** (JSON view)  
   - **derived metrics** (latency, reliability, bandwidth) as a bar chart

The current version is a **design & evaluation tool** for intent-based networking and digital-twin style edge simulations. The goal is to make it easy to reason about “what happens if I change the intent?” without manually editing low-level configs.

---

## Architecture Overview

The prototype is organised into:

- `backend/orchestrator/`
  - `main.py` – FastAPI application exposing `/` and `/intent`
  - `models.py` – Pydantic models (`IntentRequest`, `ScenarioConfig`, etc.)
  - `intent_parser.py` – Rule-based parser from text → `ScenarioConfig`
- `dashboard/`
  - `app.py` – Dash + Cytoscape + Plotly dashboard
- `scenarios/`
  - placeholder for future scenario configs
- `outputs/`
  - placeholder for logs / exports

---

## How It Works (High Level)

1. **User writes an intent** in the dashboard text area:
   - e.g. number of sites, sensors per site, link quality, protocol, objective, duration.

2. The **Dash app** sends a request to the FastAPI backend:
   ```http
   POST /intent
   {
     "text": "<intent text>"
   }
