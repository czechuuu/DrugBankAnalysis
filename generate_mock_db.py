import argparse
from utils.mock_generator import generate_mock_database

def main():
    # not the utils.parser!
    parser = argparse.ArgumentParser(description='Generate a mock database.')
    parser.add_argument('--input', type=str, default='data/drugbank_partial.xml', help='Input XML file')
    parser.add_argument('--output', type=str, default='data/mock_drugbank.xml', help='Output XML file')
    parser.add_argument('--num_mock_entries', type=int, default=10, help='Number of mock entries to generate')
    parser.add_argument('--num_real_entries', type=int, default=5, help='Number of real entries to include')

    args = parser.parse_args()

    generate_mock_database(args.input, args.output, num_mock_entries=args.num_mock_entries, num_real_entries=args.num_real_entries)

if __name__ == "__main__":
    main()
