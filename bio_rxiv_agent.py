from bio2csv import scrape_biorxiv
import pandas as pd
df=scrape_biorxiv(pages=1, base_url="https://www.biorxiv.org/search/paracetamol?page=",get_abstract=True,get_full_text=True)

print(df)

df.to_csv("biorxiv_paracetamol.csv")
