# # Entry point for orchestrator API (FastAPI/Flask stub)

# from fastapi import FastAPI
# from pydantic import BaseModel

# app = FastAPI(title="Intent Edge Network Orchestrator")


# class IntentRequest(BaseModel):
#     text: str


# @app.get("/")
# def root():
#     return {"status": "ok", "message": "Orchestrator backend is running"}


# @app.post("/intent")
# def parse_intent(req: IntentRequest):
#     # temporary dummy response – just to prove API works
#     return {
#         "original_text": req.text,
#         "parsed_config": {
#             "nodes": {"sensors": 10, "edges": 2, "cloud": 1},
#             "objective": "reliability",
#         },
#     }
from fastapi import FastAPI
from .models import IntentRequest, ScenarioConfig
from .intent_parser import parse_intent_to_config

app = FastAPI(title="Intent Edge Network Orchestrator")


@app.get("/")
def root():
    return {"status": "ok", "message": "Orchestrator backend is running"}


@app.post("/intent", response_model=ScenarioConfig)
def parse_intent(req: IntentRequest) -> ScenarioConfig:
    """
    Parse a natural language intent into a normalized ScenarioConfig.
    """
    config = parse_intent_to_config(req.text)
    return config
