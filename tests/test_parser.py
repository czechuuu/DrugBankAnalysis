import pytest
from unittest.mock import MagicMock, patch
from io import StringIO
import xml.etree.ElementTree as ET
import pandas as pd
from io import StringIO
from utils.parser import Parser
from utils.parser import Parser  # Replace 'your_module' with the actual module name

@pytest.fixture
def mock_xml_file():
    # Mock XML content similar to drugbank_partial.xml
    mock_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <drugbank xmlns="http://www.drugbank.ca">
        <drug type="biotech">
            <drugbank-id primary="true">DB00001</drugbank-id>
            <drugbank-id>BTD00024</drugbank-id>
            <name>Lepirudin</name>
            <targets>
                <target>
                    <id>T001</id>
                    <name>Thrombin</name>
                    <polypeptide id="P00734" source="Swiss-Prot">
                        <name>Hirudin</name>
                        <gene-name>F2</gene-name>
                        <locus>11p15.5</locus>
                        <cellular-location>extracellular</cellular-location>
                        <external-identifiers>
                            <external-identifier>
                                <resource>GenAtlas</resource>
                                <identifier>F2-Gene</identifier>
                            </external-identifier>
                        </external-identifiers>
                    </polypeptide>
                </target>
            </targets>
        </drug>
        <drug type="small molecule">
            <drugbank-id primary="true">DB00002</drugbank-id>
            <name>SmallMolecule</name>
        </drug>
    </drugbank>
    """
    return StringIO(mock_xml)

@pytest.fixture
def parser(mock_xml_file):
    return Parser(mock_xml_file)

def test_extract(parser):
    # Test the `extract` method
    result = parser.extract(
        prefix_path="db:targets/db:target",
        simple_fields={"target-name": "db:name"},
        nested_fields={"external-ids": "db:polypeptide/db:external-identifiers/db:external-identifier/db:identifier"}
    )
    expected = pd.DataFrame([{
        "name": "Lepirudin",
        "drugbank-id": "DB00001",
        "target-name": "Thrombin",
        "external-ids": ["F2-Gene"]
    }])
    pd.testing.assert_frame_equal(result, expected)

def test_extract_id_name_df(parser):
    # Test the `extract_id_name_df` method
    result = parser.extract_id_name_df()
    expected = pd.DataFrame({
        "id": ["DB00001", "BTD00024", "DB00002"],
        "name": ["Lepirudin", "Lepirudin", "SmallMolecule"]
    })
    pd.testing.assert_frame_equal(result, expected)

def test_extract_proteins(parser):
    # Test the `extract_proteins` method
    result = parser.extract_proteins()
    expected = pd.DataFrame([{
        "drug-name": "Lepirudin",
        "target-id": "T001",
        "source": "Swiss-Prot",
        "polypeptide-id": "P00734",
        "polypeptide-name": "Hirudin",
        "gene-name": "F2",
        "genatlas-id": "F2-Gene",
        "locus": "11p15.5",
        "chromosome": "11",
        "location": "extracellular"
    }])
    pd.testing.assert_frame_equal(result, expected)

@patch('xml.etree.ElementTree.ElementTree.parse')
def test_parser_init(mock_parse, mock_xml_file):
    # Mock the ElementTree and its root
    mock_root = ET.parse(mock_xml_file).getroot()
    mock_tree = MagicMock()
    mock_tree.getroot.return_value = mock_root
    mock_parse.return_value = mock_tree

    # Initialize the parser with the mocked parse function
    parser = Parser("mock_file.xml")

    # Assertions
    assert parser.ns == {"db": "http://www.drugbank.ca"}
    assert parser.et_root == mock_root  # Ensure the root is correctly set

def test_extract_fields_and_types_with_multiple_drugs(parser):
    """
    This test checks the parser's extract_fields_and_types method
    against multiple drugs (biotech and small molecule). Ensures
    that the returned field_data dictionary and drug_types list
    include data for both drugs.
    """
    field_data, drug_types = parser.extract_fields_and_types()
    
    # Basic structure checks
    assert isinstance(field_data, dict), "field_data should be a dictionary"
    assert isinstance(drug_types, list), "drug_types should be a list"
    
    # Check drug_types
    assert "biotech" in drug_types, "Expected 'biotech' in drug_types"
    assert "small molecule" in drug_types, "Expected 'small molecule' in drug_types"
    
    # Ensure some known fields exist
    assert "drugbank-id" in field_data, "drugbank-id key missing from field_data"
    assert "name" in field_data, "name key missing from field_data"

    # Check that known IDs appear in field_data
    all_drugbank_ids = field_data["drugbank-id"]
    assert any("DB00001" in val for val in all_drugbank_ids), "DB00001 missing in drugbank-id values"
    assert any("BTD00024" in val for val in all_drugbank_ids), "BTD00024 missing in drugbank-id values"
    assert any("DB00002" in val for val in all_drugbank_ids), "DB00002 missing in drugbank-id values"

    # Check that known names appear in the 'name' field
    all_names = field_data["name"]
    assert any("Lepirudin" in val for val in all_names), "'Lepirudin' missing in name values"
    assert any("SmallMolecule" in val for val in all_names), "'SmallMolecule' missing in name values"
