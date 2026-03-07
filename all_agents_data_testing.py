from aletheon_mvp_1.agents_old import fda_agent, pubmed_agent, trials_agent, biorxiv_agent
from schema import DrugState
import pandas as pd

state: DrugState = {
    "drug_name": "remdesivir",
    "fda_data": None,
    "pubmed_data": None,
    "trials_data": None,
    "biorxiv_df": None,
    "report": None
}

print("\n========== FDA ==========")
state = fda_agent(state)
print(state["fda_data"])
print(type(state["fda_data"]))

print("\n========== PUBMED ==========")
state = pubmed_agent(state)
print(state["pubmed_data"])

print("\n========== TRIALS ==========")
state = trials_agent(state)
print(state["trials_data"])

print("\n========== BIORXIV ==========")
state = biorxiv_agent(state)
print(state["biorxiv_df"].head)

print("\n========== DONE ==========")