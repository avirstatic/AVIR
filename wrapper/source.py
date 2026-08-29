"""
module wrapper.source: wrapper for source code analysis
"""
import os
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any
from wrapper.analyzer import AnalyzerContainer
from wrapper.apollo import ApolloManager
from utils import get_logger

logger = get_logger(__name__)

class SourceAnalyzer:
    """
    A wrapper for source code analysis in the analyzer container
    employing cloc command etc,.
    """
    analyzer: AnalyzerContainer

    def __init__(self, analyzer: AnalyzerContainer):
        """
        Constructor

        :param AnalyzerContainer analyzer: Analyzer container
        """
        self.analyzer: AnalyzerContainer = analyzer
        if not analyzer.is_running():
            if not analyzer.has_image():
                analyzer.build()
            analyzer.start()

    @staticmethod
    def get_module_folders(apollo_manager: ApolloManager, modules: List[str]) -> Dict[str, List[Path]]:
        """
        Get the dir list for each moulde in the distinct Apollo version folder
        
        :param ApolloManager apollo_manager: Apollo manager
        :param List[str] modules: list of modules
        :returns: Dictionary with module names as keys and list of dirs (abs on host) as values
        :rtype: Dict[str, List[Path]]
        """
        modules_dir = apollo_manager.apollo_root / 'modules'
        module_folders: Dict[str, List[Path]] = {}
        for module in modules:
            matches = [d for d in modules_dir.iterdir() if d.is_dir() and d.name.startswith(module)]
            if not matches:
                raise FileNotFoundError(f"No directory found for module '{module}' under {modules_dir}")
            module_folders[module] = matches
        return module_folders

    @staticmethod
    def get_folder_size(folder_path: Path) -> int:
        """
        Get the total actual size of a folder in bytes (not disk usage)
        This counts the actual file content size, not the disk blocks used

        :param Path folder_path: Path to the folder (abs on host)
        :returns: Total actual size in bytes
        :rtype: int
        """
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(folder_path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    try:
                        total_size += os.path.getsize(filepath)
                    except (OSError, FileNotFoundError):
                        continue
        except (OSError, FileNotFoundError):
            return 0
        return total_size

    @staticmethod
    def format_size(size_bytes: int) -> str:
        """
        Format size in bytes to KB or MB
        
        :param int size_bytes: Size in bytes
        :returns: Formatted size string (e.g., "1.5M" or "512K")
        :rtype: str
        """
        if size_bytes == 0:
            return "0K"
        
        # Convert to MB if >= 1024 KB
        size_mb = size_bytes / (1024 * 1024)
        if size_mb >= 1:
            return f"{size_mb:.2f}M"
        else:
            # Convert to KB
            size_kb = size_bytes / 1024
            return f"{size_kb:.2f}K"

    def get_folder_cloc(self, apollo_manager: ApolloManager, folder_path: Path) -> Optional[Dict[str, Tuple[int, int]]]:
        """
        Get the cloc information for a given folder in the distinct Apollo version
        get and only get the C++ and C/C++ Header information, note that cmd exec in the avir container

        :param ApolloManager apollo_manager: Apollo manager
        :param Path folder_path: Path to the foler (abs on host)
        :returns: Dictionary with language names as keys and (files, code) tuples as values
        :rtype: Dict[str, Tuple[int, int]]
        """
        # NOTE: the path is in the analyzer container.
        folder_name = folder_path.name
        dir_path = Path(self.analyzer.project_docker_path) / apollo_manager.apollo_root.name / "modules" / folder_name

        returncode, stdout, stderr = self.analyzer.exec(["cloc", str(dir_path)])
        if returncode != 0:
            logger.error(f"Failed to get cloc information for folder {folder_name}: {stderr}")
            return None

        # Parse the output to extract C++ and C/C++ Header information
        result_dict: Dict[str, Tuple[int, int]] = {}
        lines = (stdout or "").split("\n")

        for line in lines:
            # Look for C++ and C/C++ Header lines (skip separator lines)
            if "C++" in line and not line.startswith("---") and not line.startswith("Language"):
                # Extract all numbers from the line
                numbers = re.findall(r"\d+", line)
                if len(numbers) >= 4:  # files, blank, comment, code
                    # Extract language name (everything before the first number)
                    language_match = re.match(r"^(.+?)\s+\d+", line)
                    if language_match:
                        language = language_match.group(1).strip()
                        # Normalize language names
                        if language == "C++":
                            files = int(numbers[0])
                            code = int(numbers[3])  # code is the 4th number
                            result_dict["C++"] = (files, code)
                        elif "C/C++ Header" in language or language == "C/C++ Header":
                            files = int(numbers[0])
                            code = int(numbers[3])  # code is the 4th number
                            result_dict["C/C++ Header"] = (files, code)

        return result_dict

    def get_source_data(self, version: int, modules: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Get the source data for all modules in one version

        :param int version: version number of Apollo
        :param List[str] modules: list of modules
        :returns: Dictionary with module names as keys and data as values
        :rtype: Dict[str, Dict[str, Any]]
        """
        apollo_manager = ApolloManager(int(version))
        module_folders: Dict[str, List[Path]] = self.get_module_folders(apollo_manager, modules)
        data_dict: Dict[str, Dict[str, Any]] = {}

        for module in modules:
            cpp_files, cpp_code, header_files, header_code = 0, 0, 0, 0
            module_size = 0
            for folder in module_folders.get(module, []):
                result = self.get_folder_cloc(apollo_manager, folder)
                if result is None:
                    logger.error(f'Failed to get cloc information for module {module} in folder {folder}')
                    continue
                # Get the C++ and C/C++ Header information for the folder
                cpp_files += result.get('C++', (0, 0))[0]
                cpp_code += result.get('C++', (0, 0))[1]
                header_files += result.get('C/C++ Header', (0, 0))[0]
                header_code += result.get('C/C++ Header', (0, 0))[1]
                # Get the folder size
                module_size += self.get_folder_size(folder)
            total_files = cpp_files + header_files
            total_code = cpp_code + header_code
            # fomat the size
            formatted_size: str = self.format_size(module_size)
            # store data: tuple format is (total_code, total_files, formatted_folder_size)
            data_dict[module] = {
                'total_code': total_code,
                'total_files': total_files,
                'size': formatted_size
            }
        return data_dict
