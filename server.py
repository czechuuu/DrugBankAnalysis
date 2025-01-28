from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from utils.parser import Parser
from utils.other import get_pathway_id_df
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
        data = get_pathway_id_df(parser)
    return data

@app.post("/pathways/")
def get_pathway_count(request: DrugIDRequest, data: pd.Series = Depends(get_data)):
    """Handle POST requests to return the pathway count for a given drug ID."""
    drug_id = request.id
    if drug_id in data.index:
        return {"drug_id": drug_id, "pathway_count": int(data[drug_id])}
    else:
        raise HTTPException(status_code=404, detail=f"Drug with id {drug_id} not found.")
