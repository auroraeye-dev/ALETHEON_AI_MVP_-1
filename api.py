import json

from fastapi import FastAPI
from pydantic import BaseModel
from langgraph.graph import StateGraph, END

from schema import DrugState
from aletheon_mvp_1.agents_old import fda_agent, pubmed_agent, trials_agent, insight_agent, biorxiv_agent

app = FastAPI()

# -------- Build Graph Once --------

builder = StateGraph(DrugState)

builder.add_node("fda", fda_agent)
builder.add_node("pubmed", pubmed_agent)
builder.add_node("trials", trials_agent)
builder.add_node("biorxiv", biorxiv_agent)
builder.add_node("insight", insight_agent)

builder.set_entry_point("fda")
builder.add_edge("fda", "pubmed")
builder.add_edge("pubmed", "trials")
builder.add_edge("trials", "biorxiv")
builder.add_edge("biorxiv", "insight")
builder.add_edge("insight", END)

graph = builder.compile()

# -------- Request Schema --------

class DrugRequest(BaseModel):
    name: str

# -------- API Endpoint --------

@app.post("/drug")
def analyze_drug(req: DrugRequest):

    initial_state: DrugState = {
        "drug_name": req.name,
        "fda_data": None,
        "pubmed_data": None,
        "trials_data": None,
        "biorxiv_data": None,
        "report": None
    }

    result = graph.invoke(initial_state)

    return json.loads(result["report"])

