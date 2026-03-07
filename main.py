from langgraph.graph import StateGraph, END, START

from schema import DrugState
from agents import fda_agent, pubmed_agent, trials_agent, biorxiv_agent
from rag_node import rag_node


parralel_builder = StateGraph(DrugState)

parralel_builder.add_node("fda", fda_agent)
parralel_builder.add_node("pubmed", pubmed_agent)
parralel_builder.add_node("trials", trials_agent)
parralel_builder.add_node("biorxiv", biorxiv_agent)
parralel_builder.add_node("rag", rag_node)
parralel_builder.add_edge( START, "fda")
parralel_builder.add_edge( START, "pubmed")
parralel_builder.add_edge( START, "trials")
parralel_builder.add_edge( START, "biorxiv")
parralel_builder.add_edge("fda", "rag")
parralel_builder.add_edge("pubmed", "rag")
parralel_builder.add_edge("trials", "rag")
parralel_builder.add_edge("biorxiv", "rag")
parralel_builder.add_edge("rag", END)

graph= parralel_builder.compile()



initial_state = {
    "drug_name": "remdesivir",
    "evidence": [],
    "report": None
}

result = graph.invoke(initial_state)

png_bytes = graph.get_graph().draw_mermaid_png()

with open("graph.png", "wb") as f:
    f.write(png_bytes)

print("Graph saved as graph.png")



print("\n========== FINAL RAG REPORT ==========\n")
print(result["report"])

#save_to_document(result["report"], filename_prefix=initial_state["drug_name"])


