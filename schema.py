from typing import Annotated, List
from typing_extensions import TypedDict

def list_reducer(existing, new):
    if existing is None:
        return new
    if new is None:
        return existing
    return existing + new

class DrugState(TypedDict):
    drug_name: str
    evidence: Annotated[List[str], list_reducer]
    report: str | None