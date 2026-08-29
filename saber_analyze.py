import sys
from datetime import datetime
from wrapper.analyzer import AnalyzerContainer
from wrapper.apollo import ApolloManager
from framework.saber import SaberTool
from utils import get_logger
from config import PROJECT_ROOT

def main():
    # WARNING: Before running this script, you must have already extracted the bitcode files using the extract.py script

    logger = get_logger()

    logger.info("Starting Saber analyze...")

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
    saber_tool = SaberTool(analyzer)
    saber_tool.process(ApolloManager(version=int(version_input)))
    end_time = datetime.now()
    logger.success(f"{saber_tool.tool_name} analyze for version {version_input} completed in {end_time - start_time}")
    logger.info(f"Results saved to {PROJECT_ROOT}/results/{saber_tool.tool_name}_json_v{version_input}/")
    logger.info("Please use the semantic_statistic.py script to cluster the results!")

if __name__ == "__main__":

    main()
