import sys
from datetime import datetime
from typing import List, Dict, Tuple
from pandas import DataFrame
from framework.field import FieldExtractor
from wrapper.apollo import ApolloManager
from wrapper.analyzer import AnalyzerContainer
from framework.saber import SaberTool
from utils import get_logger
from config import MODULES

def main():

    logger = get_logger()

    logger.info("Starting semantic statistic...")

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
    field_extractor = FieldExtractor()
    f_names: List[str] = list(field_extractor.field_paths.keys())
    print("Please select the field you want to statistic:")
    for i, f_name in enumerate(f_names):
        print(f"{i+1}. {f_name}")
    selected_index = int(input("Enter the index: "))
    if selected_index < 1 or selected_index > len(f_names):
        logger.error(f"Invalid index: {selected_index}, please enter a number between 1 and {len(f_names)}")
        sys.exit(1)
    selected_field = f_names[selected_index - 1]

    result: Dict[str, Tuple[int, ...]] = field_extractor.aggregate(field_name=selected_field,
                                       apollo_manager=ApolloManager(version=int(version_input)),
                                       tool=SaberTool(AnalyzerContainer("avir-dev")),
                                       modules=MODULES)
    # Get the last field name of the field list
    field_list = [f[-1] for f in field_extractor.field_paths[selected_field]]
    # Check if the length is equal to the field list
    bad = {k: len(v) for k, v in result.items() if len(v) != len(field_list)}
    if bad:
        sample = list(bad.items())[:10]
        raise ValueError(
            f"the length of the tuple in the result is not consistent with the field_list: expected {len(field_list)}, "
            f"but {len(bad)} modules are not matched (example: {sample})"
        )

    df = DataFrame.from_dict(result, orient="index", columns=field_list)
    df.index.name = "module"
    df.to_csv(f"results/semantic_statistic_{selected_field}_v{version_input}.csv", index=True, header=True)

    end_time = datetime.now()
    logger.success(f"Semantic statistic of {selected_field} for version {version_input} completed in {end_time - start_time}")

if __name__ == '__main__':

    main()
