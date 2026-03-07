from rag import SimpleRAG

def rag_node(state):

    print("RAG NODE: Building index")

    rag = SimpleRAG()

    # state["evidence"] is list[str]
    rag.build(state["evidence"])

    answer = rag.ask("Generate a full report on the drug based on the evidence provided. Include paper ids if available, and full paper text if available. And no hallucinations.")

    return {"report": answer}