import pandas as pd
import pytest
from unittest import mock
from utils.other import get_pathway_id_df, get_id_to_synonyms_df

def test_get_pathway_id_df(mocker):
    # Mock the parser
    mock_parser = mocker.Mock()

    # Mock extract() to return a DataFrame with some pathway data
    mock_extract_df = pd.DataFrame({
        "pathway-name": ["PathwayA", "PathwayB", "PathwayB"],
        "drugs": ["DrugAlpha", "DrugBeta", "DrugBeta"]
    })
    mock_parser.extract.return_value = mock_extract_df

    # Mock extract_id_name_df() to return an id-to-name mapping
    mock_id_name_df = pd.DataFrame({
        "id": ["IDAlpha", "IDBeta"],
        "name": ["DrugAlpha", "DrugBeta"]
    })
    mock_parser.extract_id_name_df.return_value = mock_id_name_df

    # Run
    data = get_pathway_id_df(mock_parser)

    # Verify calls
    mock_parser.extract.assert_called_once()
    mock_parser.extract_id_name_df.assert_called_once()

    # Check the result
    # We should have 2 unique IDs: IDAlpha and IDBeta
    # IDAlpha has 1 pathway, IDBeta has 2
    assert len(data) == 2
    assert data.loc["IDAlpha"] == 1
    assert data.loc["IDBeta"] == 2


def test_get_pathway_id_df_no_pathways(mocker):
    # Mock the parser
    mock_parser = mocker.Mock()

    # Mock extract() to return an empty DataFrame
    mock_extract_df = pd.DataFrame(columns=["pathway-name", "drugs"])
    mock_parser.extract.return_value = mock_extract_df

    # Mock extract_id_name_df() to return an id-to-name mapping
    mock_id_name_df = pd.DataFrame({
        "id": ["IDAlpha", "IDBeta"],
        "name": ["DrugAlpha", "DrugBeta"]
    })
    mock_parser.extract_id_name_df.return_value = mock_id_name_df

    # Run
    data = get_pathway_id_df(mock_parser)

    # No pathways, so each ID has 0
    assert len(data) == 2
    assert data.loc["IDAlpha"] == 0
    assert data.loc["IDBeta"] == 0


def test_get_pathway_id_df_unmatched_drugs(mocker):
    # Mock the parser
    mock_parser = mocker.Mock()

    # Some pathway data includes a drug that doesn't appear in the id_name_df
    mock_extract_df = pd.DataFrame({
        "pathway-name": ["PathwayA", "PathwayA"],
        "drugs": ["DrugAlpha", "DrugGamma"]  # DrugGamma is extra
    })
    mock_parser.extract.return_value = mock_extract_df

    # Mock extract_id_name_df() to return known drugs
    mock_id_name_df = pd.DataFrame({
        "id": ["IDAlpha", "IDBeta"],
        "name": ["DrugAlpha", "DrugBeta"]
    })
    mock_parser.extract_id_name_df.return_value = mock_id_name_df

    # Run
    data = get_pathway_id_df(mock_parser)

    # We only match DrugAlpha -> IDAlpha
    # IDBeta has 0
    assert len(data) == 2
    assert data.loc["IDAlpha"] == 1
    assert data.loc["IDBeta"] == 0

def test_get_id_to_synonyms_df(mocker):
    mock_parser = mocker.Mock()

    # Mock parser.extract_id_name_df()
    mock_id_name_df = pd.DataFrame({
        "id": ["ID1", "ID2", "ID3"],
        "name": ["DrugA", "DrugB", "DrugC"]
    })
    mock_parser.extract_id_name_df.return_value = mock_id_name_df

    # Mock parser.extract() for synonyms
    # We must have "name" column to merge on
    mock_synonyms_df = pd.DataFrame({
        "name": ["DrugA", "DrugB", "DrugC", "DrugC"],
        "synonyms": [
            ["Alpha", "A1"], 
            ["Bravo"], 
            ["Charlie"], 
            ["C2"]
        ]
    }).explode("synonyms").reset_index(drop=True)
    mock_parser.extract.return_value = mock_synonyms_df

    # Run
    result_df = get_id_to_synonyms_df(mock_parser)

    # Verify calls
    mock_parser.extract_id_name_df.assert_called_once()
    mock_parser.extract.assert_called_once_with(".", nested_fields={'synonyms': 'db:synonyms/db:synonym'}, drug_id=None)

    # Check that returned DataFrame merges correctly
    # Expect columns: ["id", "name", "synonyms"]
    assert list(result_df.columns) == ["id", "name", "synonyms"]
    assert len(result_df) == 5  # 2 synonyms for DrugA, 1 for DrugB, 2 for DrugC
    assert result_df.loc[result_df["name"] == "DrugA", "synonyms"].tolist() == ["Alpha", "A1"]
    assert result_df.loc[result_df["name"] == "DrugB", "synonyms"].tolist() == ["Bravo"]
    assert result_df.loc[result_df["name"] == "DrugC", "synonyms"].tolist() == ["Charlie", "C2"]