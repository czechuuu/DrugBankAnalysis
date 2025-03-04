import xml.etree.ElementTree as ET
import random
import copy
from utils.parser import Parser

# Utility function to parse the XML file
def parse_xml(input_file):
    tree = ET.parse(input_file)
    return tree, tree.getroot()

# Utility function to collect namespaces
def get_namespaces():
    return {
        'db': 'http://www.drugbank.ca',
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
    }

# Function to select real drugs from the original database
def select_real_drugs(root, namespaces, num_real_entries):
    real_drugs = root.findall('db:drug', namespaces)
    return random.sample(real_drugs, min(num_real_entries, len(real_drugs)))

# Function to create a new root with copied attributes
def create_new_root(root, namespaces):
    ET.register_namespace('', namespaces['db'])  # Set default namespace
    return ET.Element('drugbank', attrib=root.attrib)

# Function to add real drugs to the mock database
def add_real_drugs(mock_root, real_drugs):
    for drug in real_drugs:
        mock_root.append(copy.deepcopy(drug))  # Deep copy to avoid altering the original tree

# Function to generate mock drugs with nested fields, including pathways
def generate_mock_drugs(mock_root, num_mock_entries, field_data, nested_field_data, drug_types):
    if not drug_types:  # Fallback if no types were found
        drug_types = ['biotech', 'small molecule']

    for i in range(1, num_mock_entries + 1):
        # Randomly select a drug type
        random_type = random.choice(drug_types)

        drug = ET.SubElement(
            mock_root,
            'drug',
            attrib={'type': random_type, 'created': '2025-01-01', 'updated': '2025-01-01'}
        )

        # Assign consecutive mock drug IDs
        ET.SubElement(drug, 'drugbank-id', attrib={'primary': 'true'}).text = f"MOCK{i:05d}"

        # Assign simple fields
        for tag, values in field_data.items():
            if values:
                ET.SubElement(drug, tag).text = random.choice(values)

        # Assign nested fields (NEW!)
        for tag, nested_values in nested_field_data.items():
            parent_element = ET.SubElement(drug, tag)
            for entry in nested_values:
                _add_nested_field(parent_element, entry)



# Function to write the combined XML tree to a file
def write_mock_database(mock_root, output_file):
    mock_tree = ET.ElementTree(mock_root)
    ET.indent(mock_tree, space="  ", level=0)  # Pretty print
    mock_tree.write(output_file, encoding='utf-8', xml_declaration=True)

def _add_nested_field(parent_element, nested_data):
    """
    Recursively add nested fields to the XML tree.
    """
    if isinstance(nested_data, dict):
        for key, values in nested_data.items():
            for value in values:
                sub_element = ET.SubElement(parent_element, key)
                _add_nested_field(sub_element, value)
    else:
        parent_element.text = nested_data  # If it's just text, add it directly


# Main function to generate the mock database
def generate_mock_database(input_file, output_file, num_mock_entries, num_real_entries):
    # Parse the input XML file
    tree, root = parse_xml(input_file)
    parser = Parser(input_file)

    # Get namespaces
    namespaces = get_namespaces()

    # Extract simple and nested fields, as well as drug types
    field_data, nested_field_data, drug_types = parser.extract_fields_and_types()

    # Select random real entries
    real_drugs = select_real_drugs(root, namespaces, num_real_entries)

    # Create a new root for the mock database
    mock_root = create_new_root(root, namespaces)

    # Add real drugs
    add_real_drugs(mock_root, real_drugs)

    # Generate mock entries (FIXED!)
    generate_mock_drugs(mock_root, num_mock_entries, field_data, nested_field_data, drug_types)

    # Write the combined database to an output file
    write_mock_database(mock_root, output_file)
    