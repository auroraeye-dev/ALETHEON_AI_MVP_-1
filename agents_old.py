from openai import OpenAI
from dotenv import load_dotenv
import os
from bio2csv import scrape_biorxiv
import pandas as pd

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

import requests
from schema import DrugState

def fda_agent(state: DrugState):
    """
    Fetch drug label data from OpenFDA.
    """

    drug = state["drug_name"]

    print(f"FDA Agent: Fetching data for {drug}")

    url = (
        "https://api.fda.gov/drug/label.json"
        f"?search=openfda.generic_name:{drug}&limit=1"
    )

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        try:
            print("FDA sample keys:", data["results"][0].keys())
            print("FDA sample keys:", data["results"][0].keys())
            print("FDA indications:", data["results"][0].get("indications_and_usage", [])[:1])
        except Exception:
            print("FDA preview unavailable")
    except Exception as e:
        print("FDA Agent error:", e)
        data = None

    # Agent returns ONLY its contribution to state
    return {
        "evidence": [str(data)]
    }
def pubmed_agent(state: DrugState):
    """
    Fetch research data from PubMed.
    """

    drug = state["drug_name"]

    print(f"PubMed Agent: Searching papers for {drug}")

    url = (
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        f"?db=pubmed&term={drug}&retmode=json"
    )

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        try:
            ids= data["esearchresult"]["idlist"]
            print("PubMed IDs:", len(ids))
            print("PubMed sample ID:", ids[:1])
        except:
            print("PubMed preview unavailable")

    except Exception as e:
        print("PubMed Agent error:", e)
        data = None

    return {
        "evidence": [str(data)]
    }
def trials_agent(state: DrugState):
    """
    Fetch clinical trial data from ClinicalTrials.gov (v2 API)
    """

    drug = state["drug_name"]

    print(f"Trials Agent: Fetching trials for {drug}")

    url = f"https://clinicaltrials.gov/api/v2/studies?query.term={drug}&pageSize=5"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        try:
            studies = data["studies"]
            print("trials found:", len(studies))
            print("sample trial condition:", studies[0]["protocolSection"]["conditionsModule"].get("conditions", []))
        except:
            print("Trials preview unavailable")
    except Exception as e:
        print("Trials Agent error:", e)
        data = None

    return {
        "evidence": [str(data)]
    }
def biorxiv_agent(state: DrugState):
    drug = state["drug_name"]

    print(f"bioRxiv Agent: Searching preprints for {drug}")
    try:

        base_url = f"https://www.biorxiv.org/search/{drug}?page="
        df= scrape_biorxiv(pages=1, base_url=base_url,get_abstract=True,get_full_text=False)
        print("bioRxiv dataframe shape:", df.shape)
    except Exception as e:
        print("bioRxiv scrape error:", e)
        df= pd.DataFrame()
    state["biorxiv_df"] = df
    return {
        "evidence": [df.to_string()]
    }
def insight_agent(state: DrugState):
    combined = "\n".join(state["evidence"])

    
    print("Insight Agent: Generating report")

    # ---- FDA extraction ----
    fda_summary = {}

    try:
        results = state["fda_data"]["results"][0]

        fda_summary = {
            "indications": results.get("indications_and_usage", []),
            "warnings": results.get("warnings", []),
            "adverse_reactions": results.get("adverse_reactions", [])
        }
    except:
        fda_summary = {}

    # ---- PubMed extraction ----
    pubmed_count = 0
    try:
        pubmed_count = len(state["pubmed_data"]["esearchresult"]["idlist"])
    except:
        pass

    # ---- Trials extraction ----
    trials = []

    try:
        studies = state["trials_data"]["studies"]
        for s in studies:
            trials.append({
                "phase": s["protocolSection"]["designModule"].get("phaseList", {}),
                "condition": s["protocolSection"]["conditionsModule"].get("conditions", [])
            })
    except:
        pass

    prompt = f"""
    You are a english Language model.

    CRITICAL RULES:

    1. You may ONLY use the data below.
    2. If the data does not contain an answer, reply exactly:
    NO DATA INGESTED
    3. Do NOT use any outside knowledge.
    4. Quote exact phrases from the context.

    CONTEXT:
    ----------------
    {combined}
    ----------------

    Answer:
    Just combine the insights from the data into a report on the drug. dont add any information that is not in the data. 
    if research papers are mentioned, include the number of papers. if drug label information is mentioned, include that information.
    clinical trials information should also be included if mentioned in the data.
    Don't use any pretrained knowledge, only use the data provided above. Not even 1 word of pretrained knowledge. 
    """



    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )

    return {
        "report": response.choices[0].message.content
    }

