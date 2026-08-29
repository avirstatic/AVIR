import sys
import os
import json
from wrapper.parse import BitcodeParser
from wrapper.analyzer import AnalyzerContainer
from utils import get_logger

def main():

    logger = get_logger()

    logger.info("Starting bitcode to source mapping...")

    # Get version input (6/7/8/9)
    if len(sys.argv) > 1:
        version_input = sys.argv[1]
    else:
        version_input = input("Enter the version number (6/7/8/9): ").strip()
    
    # Validate version input
    if version_input not in ['6', '7', '8', '9']:
        logger.error(f"Invalid version number: {version_input}, please enter 6, 7, 8 or 9")
        sys.exit(1)

    result_json = "results/bc_mapping_v" + version_input + ".json"
    if os.path.exists(result_json):
        logger.warning(f"Mapping table already exists in {result_json}, do you want to overwrite it? (y/N): ")
        answer = input().lower()
        if answer not in ['y', 'yes']:
            logger.info("Exiting...")
            sys.exit(0)
        else:
            os.unlink(result_json)
    analyzer = AnalyzerContainer("avir-dev")
    parser = BitcodeParser(analyzer)
    mapping_table = parser.mapping(int(version_input))
    with open(result_json, 'w', encoding='utf-8') as f:
        json.dump(mapping_table, f, indent=2, ensure_ascii=False)
    logger.success(f"Mapping table saved to: ./{result_json}")

if __name__ == "__main__":

    main()
