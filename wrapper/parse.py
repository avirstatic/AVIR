"""
module wrapper.parse: wrapper for bitcode parsing and source filename extraction
"""
import os
import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from wrapper.analyzer import AnalyzerContainer
from wrapper.apollo import ApolloManager
from utils import get_logger, run_cmd
from config import PROJECT_ROOT

logger = get_logger(__name__)

class BitcodeParser:
    """
    A wrapper for bitcode parsing and source filename extraction
    """
    analyzer: AnalyzerContainer
    temp_dir: str
    
    def __init__(self, analyzer: AnalyzerContainer) -> None:
        """
        Constructor for BitcodeProcessor

        :param AnalyzerContainer analyzer: Analyzer container
        """
        self.analyzer = analyzer
        if not analyzer.is_running():
            if not analyzer.has_image():
                analyzer.build()
            analyzer.start()
        self.temp_dir = "results/llvm_dis_temp"
        """temp dir for storing the temporary .ll files"""
        self.cleanup_temp()

    def cleanup_temp(self) -> bool:
        """
        Clean up the temporary ll folder, exec in the container should be better without permission
        problems

        :returns: True if the temporary directory is cleaned up successfully, False otherwise
        :rtype: bool
        """
        temp_dir_in_ctn = Path(self.analyzer.project_docker_path) / self.temp_dir
        returncode, stdout, stderr = self.analyzer.exec(["rm", "-rf", str(temp_dir_in_ctn)])
        if returncode != 0:
            logger.error(f"Failed to clean up temporary directory: {self.temp_dir}")
            return False
        return True

    @staticmethod
    def get_bitcode_names(apollo_manager: ApolloManager) -> List[str]:
        """
        Get all bitcode files in the apollo wllvm_bc directory
        
        :param ApolloManager apollo_manager: Apollo manager
        :returns: List of bitcode hash names
        :rtype: List[str]
        """
        bc_names: List[str] = []
        bc_path: Path = apollo_manager.bc_dir
        if not bc_path.exists():
            logger.error(f"No wllvm_bc folder found in the apollo {apollo_manager.version} directory")
            return []
        for file_path in bc_path.iterdir():
            if file_path.is_file() and not file_path.name.startswith('.'):
                # check if the file is a bitcode file
                returncode, stdout, stderr = run_cmd(
                    ["file", str(file_path)],
                    check=False,
                    capture=True,
                )
                if returncode != 0:
                    logger.warning(f"Failed to check file type: {file_path}: {(stderr or '').strip()}")
                    continue
                if "LLVM IR bitcode" in (stdout or ""):
                    bc_names.append(file_path.name)
        if not bc_names:
            logger.error(f"No bitcode files found in the apollo {apollo_manager.version} wllvm_bc directory")
            return []
        logger.info(f"Found {len(bc_names)} bitcode files in the apollo {apollo_manager.version} wllvm_bc directory")
        return bc_names
    
    def get_path(self, apollo_manager: ApolloManager, bc_name: str) -> Tuple[Path, Path]:
        """
        Get the absolute path of the bitcode in the analyzer container and the host machine

        :param ApolloManager apollo_manager: Apollo manager
        :param str bc_name: Bitcode hash name
        :returns: (absolute path of the bitcode in the analyzer container, absolute path of the bitcode in the host machine)
        :rtype: Tuple[Path, Path]
        """
        bc_dir_in_ctn = Path(self.analyzer.project_docker_path) / apollo_manager.apollo_root.name / "wllvm_bc" / bc_name
        bc_dir_in_hst = apollo_manager.bc_dir / bc_name
        return bc_dir_in_ctn, bc_dir_in_hst

    def bc_to_ll(self, apollo_manager: ApolloManager, bc_name: str) -> Optional[str]:
        """
        Convert bitcode file to temporary .ll file
        
        :param ApolloManager apollo_manager: Apollo manager
        :param str bc_name: Bitcode hash name
        :returns: the absolute path of the temporary .ll file in the host machine
        :rtype: Optional[str]
        """
        bc_dir_in_ctn, bc_dir_in_hst = self.get_path(apollo_manager, bc_name)
        bc_base = bc_name[:-3] if bc_name.endswith(".bc") else bc_name
        ll_filename = f"{bc_base}.ll"
        ll_dir_in_ctn = Path(self.analyzer.project_docker_path) / self.temp_dir / ll_filename
        """the absolute path of the temporary .ll file in the analyzer container"""
        ll_dir_in_hst = PROJECT_ROOT / self.temp_dir / ll_filename
        """the absolute path of the temporary .ll file in the host machine"""

        returncode, stdout, stderr = self.analyzer.exec([
            self.analyzer.llvmdis10_dir,
            str(bc_dir_in_ctn),
            "-o",
            str(ll_dir_in_ctn),
        ])
        if returncode != 0:
            logger.error(f"Failed to convert bitcode to .ll file: {bc_name}")
            return None
        if not os.path.exists(ll_dir_in_hst):
            logger.error(f"Failed to convert bitcode to .ll file: {bc_name}")
            return None
        return str(ll_dir_in_hst)

    def extract_source_filename(self, ll_dir_in_hst: str) -> str:
        """
        Extract source_filename information from .ll file
        
        :param str ll_dir_in_hst: The absolute path of the .ll file in the host machine
        :returns: Source filename
        :rtype: str
        """
        try:
            source_filename_re = re.compile(r'^\s*source_filename\s*=\s*"([^"]+)"\s*$')
            # usually format is: !0 = !{!"source_filename", !"filename.c"}
            metadata_source_filename_re = re.compile(r'!"source_filename",\s*!"([^"]+)"')
            # Example: !DIFile(filename: "foo.c", directory: "/path/to")
            difile_re = re.compile(
                r'!DIFile\(\s*filename:\s*"([^"]+)"(?:,\s*directory:\s*"([^"]+)")?'
            )

            metadata_fallback_re_list = [
                re.compile(r'!"([^"]+\.c)"'),
                re.compile(r'!"([^"]+\.cpp)"'),
                re.compile(r'!"([^"]+\.cc)"'),
            ]

            with open(ll_dir_in_hst, 'r', encoding='utf-8', errors='ignore') as f:
                # Pass 1: parse the source_filename = "..." at the top of the .ll file
                # this field usually appears in the first 300 lines of the file and is the most obvious
                for _ in range(300):
                    line = f.readline()
                    if not line:
                        break
                    m = source_filename_re.search(line)
                    if m:
                        return m.group(1).strip()

                # Pass 2: fallback to metadata/debug information (scan line by line to avoid reading the whole file into memory)
                f.seek(0)
                for line in f:
                    m = metadata_source_filename_re.search(line)
                    if m:
                        return m.group(1).strip()

                    m = difile_re.search(line)
                    if m:
                        filename = (m.group(1) or "").strip()
                        directory = (m.group(2) or "").strip()
                        if filename and directory and not os.path.isabs(filename):
                            return str(Path(directory) / filename)
                        if filename:
                            return filename

                    for re_obj in metadata_fallback_re_list:
                        m = re_obj.search(line)
                        if m:
                            return m.group(1).strip()
            
            logger.warning(f"Failed to extract source filename from {ll_dir_in_hst}")
            return "unknown"
            
        except Exception as e:
            logger.error(f"Failed to read file: {ll_dir_in_hst}: {e}")
            return "error"

    def mapping(self, version_input: int) -> Dict[str, str]:
        """
        Process all bitcode files in the directory and build mapping table
        
        :param int version_input: Version number of Apollo to parse the bitcode files
        :returns: Dictionary mapping bitcode hash name to source filename
        :rtype: Dict[str, str]
        """
        apollo_manager = ApolloManager(int(version_input))
        assert apollo_manager.apollo_root.exists(), f"Apollo version {version_input} directory does not exist, please reclone the corresponding version"
        bc_names = self.get_bitcode_names(apollo_manager)
        os.makedirs(PROJECT_ROOT / self.temp_dir, exist_ok=True)
        mapping_table = {}
        for bc_name in bc_names:
            ll_dir_in_hst = self.bc_to_ll(apollo_manager, bc_name)
            if ll_dir_in_hst:
                source_filename = self.extract_source_filename(ll_dir_in_hst)
                logger.info(f"Source filename: {source_filename} for bitcode: {bc_name} in version {apollo_manager.version}")
                if source_filename != "unknown" and source_filename != "error":
                    mapping_table[bc_name] = source_filename
                else:
                    mapping_table[bc_name] = "conversion_failed"
            else:
                mapping_table[bc_name] = "conversion_failed"
        
        self.cleanup_temp()
        return mapping_table

    @staticmethod
    def _parse_instcount_stats(stats_output: str) -> Tuple[int, int, int]:
        """
        Parse LLVM `-stats` output produced by the instcount pass.

        LLVM typically prints stats to stderr. Expected lines look like:
            "  66 instcount      - Number of instructions (of all types)"
        """
        total_insts: Optional[int] = None
        num_basic_blocks: Optional[int] = None
        num_functions: Optional[int] = None

        for line in (stats_output or "").splitlines():
            if "instcount" not in line:
                continue

            # Be tolerant to spacing/format; just require "<num> instcount" on the line.
            m = re.search(r"^\s*(\d+)\s+instcount\b", line)
            if not m:
                continue
            val = int(m.group(1))

            if "Number of instructions (of all types)" in line:
                total_insts = val
            elif "Number of basic blocks" in line:
                num_basic_blocks = val
            elif "Number of non-external functions" in line:
                num_functions = val

        # If some keys are missing (format change, stripped stats, etc.), keep partial results.
        return (
            total_insts if total_insts is not None else 0,
            num_basic_blocks if num_basic_blocks is not None else 0,
            num_functions if num_functions is not None else 0,
        )

    def inst_count(self, apollo_manager: ApolloManager, bc_name: str) -> Tuple[int, int, int]:
        """
        Parse the inst count from the bitcode file, using the opt command in the analyzer container

        :param ApolloManager apollo_manager: Apollo manager
        :param str bc_name: Bitcode hash name
        :returns: (total_insts, num of basic_blocks, num of non-external functions)
        :rtype: Tuple[int, int, int]
        """
        bc_dir_in_ctn, _ = self.get_path(apollo_manager, bc_name)

        logger.info(f"Parsing inst count for bitcode: {bc_name} in version {apollo_manager.version}")
        # Different LLVM versions / pass managers use different flags.
        # Try a small set of known-good invocations to be robust.
        candidate_argvs: List[List[str]] = [
            # Legacy PM (common in LLVM <= 12)
            [self.analyzer.opt10_dir, "-instcount", "-disable-output", "-stats", str(bc_dir_in_ctn)],
            # New PM (commonly: -passes=..., sometimes requires enabling new PM)
            [self.analyzer.opt10_dir, "-enable-new-pm=1", "-passes=instcount", "-disable-output", "-stats", str(bc_dir_in_ctn)],
            [self.analyzer.opt10_dir, "-enable-new-pm=1", "--passes=instcount", "-disable-output", "-stats", str(bc_dir_in_ctn)],
        ]

        last_err: Optional[str] = None
        for argv in candidate_argvs:
            returncode, stdout, stderr = self.analyzer.exec(argv)
            if returncode != 0:
                last_err = (stderr or stdout or "").strip()
                continue

            # NOTE: LLVM `-stats` output is typically written to stderr.
            stats_output = (stderr or "").strip() or (stdout or "").strip()
            if not stats_output:
                logger.warning(
                    f"bitcode: {bc_name} in version {apollo_manager.version} produced empty -stats output"
                )
                return (0, 0, 0)

            total_insts, num_basic_blocks, num_functions = self._parse_instcount_stats(stats_output)
            if total_insts == 0 and num_basic_blocks == 0 and num_functions == 0:
                # Could be truly empty/metadata-only, or output format changed.
                logger.warning(
                    f"bitcode: {bc_name} in version {apollo_manager.version} did not yield instcount stats"
                )
            return (total_insts, num_basic_blocks, num_functions)

        logger.error(
            f"Failed to parse inst count from bitcode: {bc_name} in version {apollo_manager.version}"
            + (f": {last_err}" if last_err else "")
        )
        return (0, 0, 0)

    def get_module_bc(self, apollo_manager: ApolloManager, module: str) -> List[str]:
        """
        Get the bitcode file list of the distinct module in one Apollo version

        :param ApolloManager apollo_manager: Apollo manager
        :param str module: Module name
        :returns: List of bitcode hash names
        :rtype: List[str]
        """
        mapping_table = "bc_mapping_v" + str(apollo_manager.version) + ".json"
        mapping_dir = PROJECT_ROOT / "results" / mapping_table
        bc_module_list = []
        if not mapping_dir.exists():
            logger.error(f"Mapping table not found: {mapping_table}")
            logger.error("Please run name_mapping.py first to generate the mapping table!")
            return []
        with open(mapping_dir, 'r', encoding='utf-8', errors='ignore') as f:
            mapping = json.load(f)
        for hash_name, source_name in mapping.items():
            if source_name.startswith(f'modules/{module}'):
                bc_module_list.append(hash_name)
        if not bc_module_list:
            logger.warning(f"No bitcode files found for module: {module} in version {apollo_manager.version}")
            return []
        return bc_module_list
