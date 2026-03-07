import requests
import pandas as pd
from bio2csv import scrape_biorxiv
from schema import DrugState


# ---------------- FDA ----------------

def fda_agent(state: DrugState):

    drug = state["drug_name"]
    print(f"FDA Agent: {drug}")

    url = f"https://api.fda.gov/drug/label.json?search=openfda.generic_name:{drug}&limit=1"

    try:
        r = requests.get(url, timeout=10)
        data = r.json()["results"][0]

        text = f"""
FDA LABEL

Indications:
{data.get("indications_and_usage", "")}

Mechanism:
{data.get("mechanism_of_action", "")}

Warnings:
{data.get("warnings_and_cautions", "")}
"""

    except Exception as e:
        print("FDA error:", e)
        text = ""

    return {
    "evidence": [
        "FDA_LABEL_SECTION\n"
        f"Indications: {data.get('indications_and_usage','')}\n"
        f"Mechanism: {data.get('mechanism_of_action','')}\n"
        f"Warnings: {data.get('warnings_and_cautions','')}"
    ]
}


# ---------------- PUBMED ----------------

def pubmed_agent(state: DrugState):

    drug = state["drug_name"]
    print(f"PubMed Agent: {drug}")

    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={drug}&retmode=json"

    try:
        r = requests.get(url, timeout=10).json()
        ids = r["esearchresult"]["idlist"]

        text = f"PUBMED IDS ({len(ids)} papers): {ids[:20]}"

    except Exception as e:
        print("PubMed error:", e)
        text = ""

    return {"evidence": [text]}


# ---------------- CLINICAL TRIALS ----------------

def trials_agent(state: DrugState):

    drug = state["drug_name"]
    print(f"Trials Agent: {drug}")

    url = f"https://clinicaltrials.gov/api/v2/studies?query.term={drug}&pageSize=5"

    try:
        r = requests.get(url, timeout=10).json()
        studies = r["studies"]

        rows = []

        for s in studies:
            rows.append(
                f"Phase: {s['protocolSection']['designModule'].get('phaseList')}, "
                f"Condition: {s['protocolSection']['conditionsModule'].get('conditions')}"
            )

        text = "CLINICAL TRIALS:\n" + "\n".join(rows)

    except Exception as e:
        print("Trials error:", e)
        text = ""

    return {"evidence": [text]}


# ---------------- BIORXIV ----------------

def biorxiv_agent(state: DrugState):

    drug = state["drug_name"]
    print(f"bioRxiv Agent: {drug}")

    try:
        df = scrape_biorxiv(
            pages=1,
            base_url=f"https://www.biorxiv.org/search/{drug}?page=",
            get_abstract=True,
            get_full_text=False
        )

        df = df[["Title", "Abstract"]].head(5)

        text = "BIORXIV PAPERS:\n" + df.to_string()

    except Exception as e:
        print("bioRxiv error:", e)
        text = ""

    return {"evidence": [text]}