"""
module framework.abstool: abstract tool class for static analysis tools
"""
import shutil
import json
from pathlib import Path
from typing import Optional, Dict
from abc import ABC, abstractmethod
from wrapper.analyzer import AnalyzerContainer
from wrapper.svf import SVFManager
from wrapper.apollo import ApolloManager
from config import PROJECT_ROOT
from utils import get_logger

logger = get_logger(__name__)

class AbstractTool(ABC):
    """
    Abstract tool class for static analysis tools.
    """
    svf_manager: SVFManager
    path: Path
    tool_name: str

    def __init__(self, analyzer: AnalyzerContainer, name: str) -> None:
        """
        Constructor

        :param AnalyzerContainer analyzer: Analyzer container
        :param str name: the name of the tool
        """
        self.svf_manager = SVFManager(analyzer)
        if name not in self.svf_manager.tools.keys():
            raise ValueError(f"Invalid tool name: {name}")
        self.path: Path = self.svf_manager.tools.get(name)
        """the path of the tool in the analyzer container"""
        self.tool_name = self.path.name if isinstance(self.path, Path) else "tool"
        """the name of the tool"""

    @abstractmethod
    def get_result(self, apollo_manager: ApolloManager, bc_name: str) -> Optional[str]:
        """
        Get the result of the tool by analyzing the bitcode file

        :param ApolloManager apollo_manager: Apollo manager
        :param str bc_name: Bitcode hash name
        :returns: the result of the tool
        :rtype: Optional[str]
        """
        pass

    def check_json_dir(self, apollo_manager: ApolloManager) -> None:
        """
        Check if the JSON directory exists for the given Apollo version
        
        :param ApolloManager apollo_manager: Apollo manager
        """
        tool_name = self.path.name if isinstance(self.path, Path) else "tool"
        tool_json_dir = PROJECT_ROOT / "results" / f"{tool_name}_json_v{apollo_manager.version}"

        # Ensure parent exists (e.g., PROJECT_ROOT/results).
        tool_json_dir.parent.mkdir(parents=True, exist_ok=True)

        if tool_json_dir.exists():
            if not tool_json_dir.is_dir():
                raise NotADirectoryError(f"JSON output path exists but is not a directory: {tool_json_dir}")
            answer = input(
                f"The JSON directory {tool_json_dir} already exists, do you want to delete it? (y/N): "
            ).strip().lower()
            if answer == "y" or answer == "yes":
                shutil.rmtree(tool_json_dir)
                tool_json_dir.mkdir(parents=True, exist_ok=True)
            return

        tool_json_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    @abstractmethod
    def to_dict(stdout: str) -> Dict:
        """
        Parse the stdout to a dictionary

        :param str stdout: the result of the tool (stdout)
        :returns: the dictionary of the result
        :rtype: Dict
        """
        pass

    def to_json(self, apollo_manager: ApolloManager, bc_name: str, stdout: Optional[str]) -> bool:
        """
        Convert the result to a json file

        :param ApolloManager apollo_manager: Apollo manager
        :param str bc_name: Bitcode hash name
        :param Optional[str] stdout: the stdout of the tool
        :returns: True if saved successfully, False otherwise
        :rtype: bool
        """
        if stdout is None:
            logger.error(f"Using {self.path.name}, failed to write {bc_name} in version {apollo_manager.version} to JSON file: stdout is None")
            return False
        try:
            data = self.to_dict(stdout)
            tool_json_dir = PROJECT_ROOT / "results" / f"{self.tool_name}_json_v{apollo_manager.version}"
            tool_json_dir.mkdir(parents=True, exist_ok=True)
            json_file = tool_json_dir / f"{bc_name}.json"

            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            logger.success(f"Using {self.tool_name}, saved {bc_name} in version {apollo_manager.version} to JSON file: {json_file}")
            return True
        except Exception as e:
            logger.error(f"Using {self.tool_name}, failed to write {bc_name} in version {apollo_manager.version} to JSON file: {type(e).__name__}: {e}")
            return False

    @abstractmethod
    def process(self, apollo_manager: ApolloManager) -> None:
        """
        Process batch of bitcode files in one version

        :param ApolloManager apollo_manager: Apollo manager
        """
        pass
