from IPython.display import Image, display
from word_doc_write import save_to_document

from langgraph.graph import StateGraph, END
from schema import DrugState
from aletheon_mvp_1.agents_old import fda_agent, pubmed_agent, trials_agent, biorxiv_agent, insight_agent

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

initial_state = {
    "drug_name": "remdesivir",
    "evidence": [],
    "report": None
}

result = graph.invoke(initial_state)
png_bytes = graph.get_graph().draw_mermaid_png()

with open("graph_1.png", "wb") as f:
    f.write(png_bytes)

print("Graph saved as graph.png")


print("\n================ FINAL DRUG REPORT ================\n")
print(result["report"])

#save_to_document(result["report"], filename_prefix=initial_state["drug_name"])
