from langgraph.graph import StateGraph, END
from schema import DrugState
from aletheon_mvp_1.agents_old import insight_agent, fda_agent, pubmed_agent, trials_agent, biorxiv_agent

builder = StateGraph(DrugState)
builder.add_node("biorxiv", biorxiv_agent)
builder.add_node("trial_agent", trials_agent)
builder.add_node("insight", insight_agent)

builder.set_entry_point("biorxiv")
builder.add_edge("biorxiv", "trial_agent")
builder.add_edge("trial_agent", "insight")
builder.add_edge("insight", END)

graph = builder.compile()

initial_state = {
    "drug_name": "remdesivir",
    "evidence": [],          # 👈 EMPTY ON PURPOSE
    "report": None
}

result = graph.invoke(initial_state)

print("\n=========== MODEL OUTPUT ===========\n")
print(result["report"])