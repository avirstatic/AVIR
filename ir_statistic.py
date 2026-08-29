import sys
from config import MODULES
from pandas import DataFrame
from datetime import datetime
from wrapper.parse import BitcodeParser
from wrapper.analyzer import AnalyzerContainer
from wrapper.apollo import ApolloManager
from utils import get_logger

def main():
    # WARNING: Before running this script, you must have already run the extract.py for the bitcode
    # extraction and name_mapping.py to geneate the correspoding mapping table!

    logger = get_logger()

    logger.info("Starting IR statistic...")

    # Get version input (6/7/8/9)
    if len(sys.argv) > 1:
        version_input = sys.argv[1]
    else:
        version_input = input("Enter the version number (6/7/8/9): ").strip()
    
    # Validate version input
    if version_input not in ['6', '7', '8', '9']:
        logger.error(f"Invalid version number: {version_input}, please enter 6, 7, 8 or 9")
        sys.exit(1)

    start_time = datetime.now()
    analyzer = AnalyzerContainer("avir-dev")
    parser = BitcodeParser(analyzer)
    apollo_manager = ApolloManager(version=int(version_input))
    result_dict = {}
    for module in MODULES:
        bc_module_list = parser.get_module_bc(apollo_manager, module)
        total_insts = 0
        total_basic_blocks = 0
        total_functions = 0
        for bc_file in bc_module_list:
            i, b, f = parser.inst_count(apollo_manager, bc_file)
            total_insts += i
            total_basic_blocks += b
            total_functions += f
        result_dict[module] = {
            'total_insts': total_insts,
            'basic_blocks': total_basic_blocks,
            'non_external_functions': total_functions
        }
    end_time = datetime.now()
    logger.success(f"IR statistic for version {version_input} completed in {end_time - start_time}")

    df = DataFrame.from_dict(result_dict, orient="index")
    df.index.name = "module"
    df.to_csv("results/ir_statistic_v" + version_input + ".csv", index=True, header=True)

if __name__ == "__main__":

    main()
