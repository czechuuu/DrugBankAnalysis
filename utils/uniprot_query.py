import requests
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
from datetime import datetime
import time

# Base UniProt API URL
UNIPROT_API_URL = "https://rest.uniprot.org/uniprotkb/search"

def fetch_uniprot(polypeptide_names):
    """Fetches the creation dates of proteins given a list of polypeptide names."""
    creation_dates = []
    families = set()

    for name in polypeptide_names:
        query = f"protein_name={name}"
        params = {
            "query": query,
            "fields": "date_created,protein_families",
            "format": "json"
        }

        try:
            response = requests.get(UNIPROT_API_URL, params=params)
            response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)
            data = response.json()

            for result in data.get("results", []):
                # Dates
                date_str = result["entryAudit"]["firstPublicDate"]
                creation_dates.append(date_str)
                # and Families
                for comment in result.get("comments", []):
                    if comment.get("commentType") == "SIMILARITY":
                        for text in comment.get("texts", []):
                            family = text.get("value")
                            if family:
                                families.add(family)


            # time.sleep(1)  # Pause to avoid rate limits

        except requests.RequestException as e:
            print(f"Error fetching data for {name}: {e}")

    creation_years = [datetime.strptime(date, "%Y-%m-%d").year for date in creation_dates]
    return creation_years, families