from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from utils.parser import Parser
import pandas as pd

app = FastAPI()

# Define the input schema for the POST request
class DrugIDRequest(BaseModel):
    id: str

# Global parser and data placeholders
FILE_NAME = "data/drugbank_partial.xml"
parser = Parser(FILE_NAME)
data = None

def get_data() -> pd.Series:
    """Prepares the pathway data."""
    global data
    if data is None:  # Lazy loading of data
        prefix = "db:pathways/db:pathway"
        simple = {"pathway-name": "db:name"}
        nested = {"drugs": "db:drugs/db:drug/db:name"}
        pathways_df = parser.extract(
            prefix,
            simple_fields=simple, 
            nested_fields=nested,
            drug_id=None,
            drug_name=None
        ).explode("drugs")

        id_name_df = parser.extract_id_name_df()

        id_pathways_df = pd.merge(
            id_name_df, 
            pathways_df, 
            left_on="name", 
            right_on="drugs",
            how="left"
        ).drop(columns=["name", "drugs"])

        id_no_pathways = id_pathways_df.groupby("id")['pathway-name'].count()
        id_no_pathways.sort_values(ascending=False, inplace=True)
        data = id_no_pathways
    return data

@app.post("/pathways/")
def get_pathway_count(request: DrugIDRequest, data: pd.Series = Depends(get_data)):
    """Handle POST requests to return the pathway count for a given drug ID."""
    drug_id = request.id
    if drug_id in data.index:
        return {"drug_id": drug_id, "pathway_count": int(data[drug_id])}
    else:
        raise HTTPException(status_code=404, detail=f"Drug with id {drug_id} not found.")
