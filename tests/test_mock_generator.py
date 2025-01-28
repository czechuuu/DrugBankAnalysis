import pytest
from io import StringIO
from unittest.mock import MagicMock, patch
from utils.parser import Parser

import xml.etree.ElementTree as ET
from utils.mock_generator import (
    parse_xml,
    get_namespaces,
    select_real_drugs,
    create_new_root,
    add_real_drugs,
    generate_mock_drugs,
    write_mock_database,
    generate_mock_database,
)

def test_parse_xml():
    xml_content = """<root><child>Test</child></root>"""
    fake_file = StringIO(xml_content)
    tree, root = parse_xml(fake_file)
    assert isinstance(tree, ET.ElementTree)
    assert root.tag == "root"
    assert root.find("child").text == "Test"

def test_get_namespaces():
    ns = get_namespaces()
    assert "db" in ns
    assert ns["db"] == "http://www.drugbank.ca"

def test_select_real_drugs():
    xml_content = """<drugbank xmlns="http://www.drugbank.ca">
        <drug/>
        <drug/>
        <drug/>
    </drugbank>"""
    root = ET.fromstring(xml_content)
    ns = {"db": "http://www.drugbank.ca"}
    selected = select_real_drugs(root, ns, 2)
    assert len(selected) == 2

def test_create_new_root():
    root = ET.Element("drugbank", attrib={"version": "1.0"})
    ns = {"db": "http://www.drugbank.ca"}
    new_root = create_new_root(root, ns)
    assert new_root.tag == "drugbank"
    assert new_root.attrib.get("version") == "1.0"

def test_add_real_drugs():
    mock_root = ET.Element("drugbank")
    drug1 = ET.Element("drug", attrib={"type": "biotech"})
    drug2 = ET.Element("drug", attrib={"type": "small molecule"})
    add_real_drugs(mock_root, [drug1, drug2])
    assert len(mock_root.findall("drug")) == 2

def test_generate_mock_drugs():
    mock_root = ET.Element("drugbank")
    field_data = {"name": ["DrugA", "DrugB"], "description": ["DescA", "DescB"]}
    drug_types = ["biotech", "small molecule"]
    generate_mock_drugs(mock_root, 2, field_data, drug_types)
    drugs = mock_root.findall("drug")
    assert len(drugs) == 2
    assert any("MOCK00001" in d.find("drugbank-id").text for d in drugs)

@patch("xml.etree.ElementTree.ElementTree.write")
def test_write_mock_database(mock_write):
    mock_root = ET.Element("drugbank")
    write_mock_database(mock_root, "output.xml")
    mock_write.assert_called_once()

@patch("utils.mock_generator.write_mock_database")
@patch("utils.mock_generator.add_real_drugs")
@patch("utils.mock_generator.select_real_drugs")
@patch("utils.mock_generator.create_new_root")
@patch("utils.mock_generator.generate_mock_drugs")
@patch("utils.mock_generator.parse_xml")
def test_generate_mock_database(
    mock_parse, mock_gen, mock_new_root, mock_select, mock_add, mock_write
):
    # Mock data
    fake_tree = MagicMock()
    fake_root = ET.Element("drugbank")
    mock_parse.return_value = (fake_tree, fake_root)
    returned_root = ET.Element("drugbank")
    mock_new_root.return_value = returned_root
    # Run function
    generate_mock_database("data/drugbank_partial.xml", "data/test_mock_output.xml", 2, 1)
    # Assertions
    mock_parse.assert_called_once()
    mock_select.assert_called_once()
    mock_new_root.assert_called_once()
    mock_add.assert_called_once()
    mock_gen.assert_called_once()
    mock_write.assert_called_once_with(returned_root, "data/test_mock_output.xml")
    