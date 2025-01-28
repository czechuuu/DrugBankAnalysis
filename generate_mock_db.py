from utils.mock_generator import generate_mock_database

if __name__ == "__main__":
    generate_mock_database('data/drugbank_partial.xml', 'data/mock_drugbank.xml', num_mock_entries=10, num_real_entries=5)
