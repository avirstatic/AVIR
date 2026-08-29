import sys
from datetime import datetime
from pandas import DataFrame
from wrapper.source import SourceAnalyzer
from wrapper.analyzer import AnalyzerContainer
from utils import get_logger
from config import MODULES

def main():

    logger = get_logger()

    logger.info("Starting source statistic...")

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
    source_analyzer = SourceAnalyzer(analyzer)
    data_dict = source_analyzer.get_source_data(int(version_input), MODULES)
    end_time = datetime.now()
    logger.success(f"Source level statistic for version {version_input}.0 completed in {end_time - start_time}")

    df = DataFrame.from_dict(data_dict, orient="index")
    df.index.name = "module"
    df.to_csv("results/source_statistic_v" + version_input + ".csv", index=True, header=True)
    logger.info(f"the statistic result is saved to ./results/source_statistic_v{version_input}.csv")

if __name__ == "__main__":

    main()
