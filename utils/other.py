import pandas as pd
from utils.parser import Parser

def get_pathway_id_df(parser: Parser):
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
    return id_no_pathways
