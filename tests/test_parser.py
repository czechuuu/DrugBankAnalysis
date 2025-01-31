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


def test_extract_fields_and_types(parser):
    """Test extract_fields_and_types to ensure it extracts simple & nested fields correctly."""
    field_data, nested_field_data, drug_types = parser.extract_fields_and_types()

    # Check extracted drug types
    assert "biotech" in drug_types, "Expected 'biotech' in drug_types"
    assert "small molecule" in drug_types, "Expected 'small molecule' in drug_types"

    # Check basic field extraction
    assert "drugbank-id" in field_data, "Missing 'drugbank-id' in extracted fields"
    assert "name" in field_data, "Missing 'name' in extracted fields"
    assert "Lepirudin" in field_data["name"], "'Lepirudin' missing from extracted names"
    assert "DB00001" in field_data["drugbank-id"], "'DB00001' missing from extracted IDs"

    # Check nested field extraction (e.g., targets)
    assert "targets" in nested_field_data, "Missing 'targets' in nested field extraction"
