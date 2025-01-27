import xml.etree.ElementTree as ET
import random
import copy

def generate_mock_database(input_file, output_file, num_mock_entries, num_real_entries):
    # Parse the input XML file
    tree = ET.parse(input_file)
    root = tree.getroot()

    # Define the namespaces
    namespaces = {
        'db': 'http://www.drugbank.ca',
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
    }

    # Extract all fields for random selection
    field_data = {}
    for drug in root.findall('db:drug', namespaces):
        for field in drug:
            tag = field.tag.split('}')[-1]  # Get the field's local name without namespace
            if tag not in field_data:
                field_data[tag] = []
            if field.text and field.text.strip():  # Avoid empty or None fields
                field_data[tag].append(field.text.strip())

            # Handle nested fields
            for subfield in field:
                subtag = subfield.tag.split('}')[-1]
                if subtag not in field_data:
                    field_data[subtag] = []
                if subfield.text and subfield.text.strip():
                    field_data[subtag].append(subfield.text.strip())

    # Select random real entries from the original database
    real_drugs = root.findall('db:drug', namespaces)
    selected_real_drugs = random.sample(real_drugs, min(num_real_entries, len(real_drugs)))

    # Create a new root for the mock database
    ET.register_namespace('', namespaces['db'])  # Set default namespace
    mock_root = ET.Element('drugbank', attrib=root.attrib)

    # Add real entries to the mock database
    for drug in selected_real_drugs:
        mock_root.append(copy.deepcopy(drug))  # Deep copy to avoid altering the original tree

    # Generate mock entries
    for i in range(1, num_mock_entries + 1):
        drug = ET.SubElement(mock_root, 'drug', attrib={'type': 'biotech', 'created': '2025-01-01', 'updated': '2025-01-01'})

        # Assign consecutive mock drug IDs
        ET.SubElement(drug, 'drugbank-id', attrib={'primary': 'true'}).text = f"MOCK{i:05d}"

        # Randomly assign values to all available fields
        for tag, values in field_data.items():
            if values:  # Only add tags with available data
                ET.SubElement(drug, tag).text = random.choice(values)

    # Write the combined database to an output file
    mock_tree = ET.ElementTree(mock_root)
    ET.indent(mock_tree, space="  ", level=0)  # Pretty print
    mock_tree.write(output_file, encoding='utf-8', xml_declaration=True)

# Usage example
generate_mock_database('data/drugbank_partial.xml', 'data/mock_drugbank.xml', num_mock_entries=10, num_real_entries=5)
