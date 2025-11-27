# Entry point for orchestrator API (FastAPI/Flask stub)

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Intent Edge Network Orchestrator")


class IntentRequest(BaseModel):
    text: str


@app.get("/")
def root():
    return {"status": "ok", "message": "Orchestrator backend is running"}


@app.post("/intent")
def parse_intent(req: IntentRequest):
    # temporary dummy response – just to prove API works
    return {
        "original_text": req.text,
        "parsed_config": {
            "nodes": {"sensors": 10, "edges": 2, "cloud": 1},
            "objective": "reliability",
        },
    }
