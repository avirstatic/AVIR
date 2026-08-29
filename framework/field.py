"""
module framework.field: wrapper for json field extraction
"""
import json
from pathlib import Path
from typing import Any, Optional, Sequence, Tuple, Union, Dict, List
from utils import get_logger
from wrapper.apollo import ApolloManager
from framework.abstool import AbstractTool
from config import PROJECT_ROOT

logger = get_logger(__name__)

class FieldExtractor:
    """
    A wrapper for json field extraction from the static analysis json files

    This class is a singleton class, only one instance should be created.
    """
    __initialized: bool
    field_paths: Dict[str, List[Tuple[str, ...]]]

    _instance = None

    def __new__(cls):
        """
        This class is a Singleton Design Pattern, override the .__new__()
        """
        if cls._instance is None:
            cls._instance = super(FieldExtractor, cls).__new__(cls)
            cls._instance.__initialized = False
        return cls._instance

    def __init__(self):
        """
        Constructor
        """
        if not self.__initialized:
            self.__initialized = True

        self.field_paths = {
            "abs_scale": [
                ("General Stats", "TotalObjects"),
                ("General Stats", "TotalPointers"),
                ("General Stats", "TotalSVFStmts"),
            ],
            "pt_complex": [
                ("General Stats", "AddrsNum"),
                ("General Stats", "GepsNum"),
                ("Andersen Pointer Analysis Stats", "Numbers stats", "NumOfLoads"),
                ("Andersen Pointer Analysis Stats", "Numbers stats", "NumOfStores"),
                ("Andersen Pointer Analysis Stats", "Numbers stats", "NumOfCopys"),
            ],
            "obj_ingredient": [
                ("General Stats", "HeapObjs"),
                ("General Stats", "StackObjs"),
                ("General Stats", "GlobalObjs"),
                ("General Stats", "FunctionObjs"),
            ],
            "call_graph": [
                ("PTACallGraph Stats (Andersen analysis)", "Numbers stats", "TotalNode"),
                ("PTACallGraph Stats (Andersen analysis)", "Numbers stats", "TotalEdge"),
                ("PTACallGraph Stats (Andersen analysis)", "Numbers stats", "TotalCycle"),
            ],
            "svf_statistic": [
                ("SVFG Statistics", "Numbers stats", "TotalNode"),
                ("SVFG Statistics", "Numbers stats", "TotalEdge"),
                ("SVFG Statistics", "Numbers stats", "DirectEdge"),
                ("SVFG Statistics", "Numbers stats", "IndirectEdge"),
            ],
            "formal_dep": [
                ("SVFG Statistics", "Numbers stats", "FormalIn"),
                ("SVFG Statistics", "Numbers stats", "FormalOut"),
                ("SVFG Statistics", "Numbers stats", "FormalParam"),
                ("SVFG Statistics", "Numbers stats", "FormalRet"),
            ],
            "actual_dep": [
                ("SVFG Statistics", "Numbers stats", "ActualIn"),
                ("SVFG Statistics", "Numbers stats", "ActualOut"),
                ("SVFG Statistics", "Numbers stats", "ActualParam"),
                ("SVFG Statistics", "Numbers stats", "ActualRet"),
            ],
            "mem_access": [
                ("Memory SSA Statistics", "Numbers stats", "MemRegions"),
                ("Memory SSA Statistics", "Numbers stats", "MSSAPhi"),
                ("Memory SSA Statistics", "Numbers stats", "LoadMuNode"),
                ("Memory SSA Statistics", "Numbers stats", "StoreChiNode"),
            ],
            "inter_mem": [
                ("Memory SSA Statistics", "Numbers stats", "FunEntryChi"),
                ("Memory SSA Statistics", "Numbers stats", "FunRetMu"),
            ],
            "pointer_mem": [
                ("Andersen Pointer Analysis Stats", "Numbers stats", "NullPointer"),
                ("Andersen Pointer Analysis Stats", "Numbers stats", "IndCallSites"),
                ("Andersen Pointer Analysis Stats", "Numbers stats", "NodesInCycles"),
            ],
        }

    @staticmethod
    def extract_fields(
        json_file: Path,
        fields: Sequence[Union[str, Sequence[str]]],
    ) -> Tuple[Any, ...]:
        """
        Extract multiple fields from a json file and return them as a tuple.

        Each field can be:
        - a dotted path string, e.g. "General Stats.TotalObjects"
        - a sequence of keys, e.g. ("General Stats", "TotalObjects")
        Missing field paths will be logged and returned as None.

        :param Path json_file: the path to the json file to be extracted
        :param Sequence[Union[str, Sequence[str]]] fields: the fields to be extracted
        :returns: a tuple of the extracted fields
        :rtype: Tuple[Any, ...]
        """
        with open(json_file, 'r') as f:
            data = json.load(f)

        def _get_by_path(root: Any, keys: Sequence[str]) -> Any:
            cur = root
            for k in keys:
                cur = cur[k]
            return cur

        values = []
        for field in fields:
            if isinstance(field, str):
                keys = field.split('.') if field else []
            else:
                keys = list(field)
            try:
                values.append(_get_by_path(data, keys))
            except (KeyError, TypeError) as e:
                logger.error(
                    f"Field path not found, using None: field={field!r}, file={json_file}, error={type(e).__name__}: {e}"
                )
                values.append(None)
        return tuple(values)

    def get_result(self, json_file: Path, field_name: str) -> Optional[Tuple[Any, ...]]:
        """
        Get the result of the fields group

        :param Path json_file: the path to the json file to be extracted
        :param str field_name: the name of the fields group
        :returns: the result of the fields group
        :rtype: Optional[Tuple[Any, ...]]
        """
        if field_name not in self.field_paths.keys():
            logger.error(f"Invalid field name: {field_name}")
            return None
        return self.extract_fields(json_file, self.field_paths[field_name])

    @staticmethod
    def cluster(apollo_manager: ApolloManager, tool: AbstractTool, module: str) -> List[Path]:
        """
        Cluster the json files by one module

        :param ApolloManager apollo_manager: Apollo manager
        :param AbstractTool tool: the json result of the tool to be clustered
        :param str module: Module name
        :returns: List of json file paths in one module of one Apollo version
        :rtype: List[Path]
        """
        mapping_file = PROJECT_ROOT / "results" / f"bc_mapping_v{apollo_manager.version}.json"
        if not mapping_file.exists():
            logger.error(f"Mapping file not found: {mapping_file}")
            logger.error("Please run name_mapping.py first to generate the mapping table!")
            return []
        # The reason why we don't call the BitcodeParser here is that using llvm-dis a little bit of time waste,
        # suggest user to run the name_mapping.py first to generate the mapping table first, rather than calling.

        json_dir = PROJECT_ROOT / "results" / f"{tool.tool_name}_json_v{apollo_manager.version}"
        if not json_dir.exists():
            raise FileNotFoundError(
                f"Result directory not found: {json_dir}. "
                f"Please make sure {tool.tool_name} json results for v{apollo_manager.version} are generated."
            )

        json_files: List[Path] = []
        missing_files: List[Path] = []
        with open(mapping_file, 'r', encoding='utf-8', errors='ignore') as f:
            mapping = json.load(f)
        for hash_name, source_name in mapping.items():
            if source_name.startswith(f'modules/{module}'):
                json_file = json_dir / f"{hash_name}.json"
                if json_file.exists():
                    json_files.append(json_file)
                else:
                    missing_files.append(json_file)

        if missing_files:
            preview = "\n".join(str(p) for p in missing_files[:10])
            raise FileNotFoundError(
                f"Missing {tool.tool_name} result json files for module={module!r}, version={apollo_manager.version}: "
                f"{len(missing_files)} files not found.\n"
                f"Examples:\n{preview}"
            )
        return json_files

    def aggregate(
        self,
        field_name: str,
        apollo_manager: ApolloManager,
        tool: AbstractTool,
        modules: Sequence[str],
    ) -> Dict[str, Tuple[int, ...]]:
        """
        Aggregate numeric values for a field group across all json files in each module,
        Missing fields are treated as None and skipped.

        :param str field_name: the name of the field group
        :param ApolloManager apollo_manager: Apollo manager
        :param AbstractTool tool: the json result of the tool to be aggregated
        :param Sequence[str] modules: list of module names to be aggregated
        :returns: a dict of module names and their aggregated values
        :rtype: Dict[str, Tuple[int, ...]]
        """
        if field_name not in self.field_paths:
            logger.error(f"Invalid field name: {field_name}")
            return {}

        n_fields = len(self.field_paths[field_name])
        result_dict: Dict[str, Tuple[int, ...]] = {}

        for module in modules:
            json_files: List[Path] = self.cluster(apollo_manager, tool, module)
            total: List[int] = [0] * n_fields

            for json_file in json_files:
                result = self.get_result(json_file, field_name)
                if not result:
                    continue

                # Be defensive about unexpected result length.
                for i, value in enumerate(result[:n_fields]):
                    if value is None:
                        continue
                    try:
                        total[i] += int(value)
                    except (TypeError, ValueError) as e:
                        logger.error(
                            f"Non-integer value skipped: field={field_name!r}, module={module!r}, "
                            f"file={json_file}, index={i}, value={value!r}, error={type(e).__name__}: {e}"
                        )

            result_dict[module] = tuple(total)

        return result_dict
