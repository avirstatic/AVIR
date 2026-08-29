"""
module framework.saber: wrapper for Saber tool
"""
from typing import Optional, Dict
from framework.abstool import AbstractTool
from framework import parse_numeric, ensure_path
from wrapper.apollo import ApolloManager
from wrapper.analyzer import AnalyzerContainer
from wrapper.parse import BitcodeParser
from utils import get_logger
from config import SECTION_LINE, PROGRAM_LINE, SUBSECTION_LINE, WRITING_LINE, KEY_VALUE_LINE

logger = get_logger(__name__)

class SaberTool(AbstractTool):
    """
    A wrapper for Saber tool to analyze the bitcode files using static analysis.

    Acknowledgement:

    - Yulei Sui, Ding Ye, and Jingling Xue. 2012.
      Static memory leak detection using full-sparse value-flow analysis.
      In Proceedings of the 2012 International Symposium on Software Testing and Analysis (ISSTA 2012).
      Association for Computing Machinery, New York, NY, USA, 254-264.
    - DOI: https://doi.org/10.1145/2338965.2336784
    """

    def __init__(self, analyzer: AnalyzerContainer) -> None:
        """
        Constructor

        :param AnalyzerContainer analyzer: Analyzer container
        """
        super().__init__(analyzer, 'saber')

    def get_result(self, apollo_manager: ApolloManager, bc_name: str) -> Optional[str]:
        """
        Get the result of the saber tool

        :param ApolloManager apollo_manager: Apollo manager
        :param str bc_name: Bitcode hash name
        :returns: the result of the saber tool
        :rtype: Optional[str]
        """
        return self.svf_manager.analyze('saber', apollo_manager, bc_name)

    @staticmethod
    def to_dict(stdout: str) -> Dict:
        """
        Parse Saber stdout string and return a structured dictionary.
        Note that Saber will print "SVFG Statistics" twice, so we need to skip the second block.
        (I think this is a bug of Saber, but we haven't reported to the author yet due to the double-blind review process)

        :param str stdout: the stdout of Saber
        :returns: the dictionary of the saber stats
        :rtype: Dict
        """
        parsed: Dict = {}
        program_id: Optional[str] = None
        current_section: Optional[str] = None
        current_subsection: Optional[str] = None
        artifacts = []

        seen_first_svfg = False
        skipping_svfg = False

        lines = (stdout or "").splitlines()
        for raw_line in lines:
            line = (raw_line or "").rstrip("\n")
            if not line.strip():
                continue

            m = SECTION_LINE.match(line)
            if m:
                section_name = m.group(1).strip()
                if section_name == "SVFG Statistics":
                    if seen_first_svfg:
                        skipping_svfg = True
                        current_section = None
                        current_subsection = None
                        continue
                    seen_first_svfg = True
                    skipping_svfg = False
                else:
                    skipping_svfg = False

                current_section = section_name
                current_subsection = None
                ensure_path(parsed, current_section, None)
                continue

            if skipping_svfg:
                continue

            m = PROGRAM_LINE.match(line)
            if m:
                program_hash = m.group(1)
                if program_id is None:
                    program_id = program_hash
                    parsed["program"] = program_id
                if current_section:
                    section_obj = ensure_path(parsed, current_section, None)
                    section_obj["program"] = program_hash
                continue

            m = SUBSECTION_LINE.match(line)
            if m:
                current_subsection = m.group(1).strip()
                ensure_path(parsed, current_section, current_subsection)
                continue

            m = WRITING_LINE.match(line)
            if m:
                artifacts.append(m.group(1))
                continue

            m = KEY_VALUE_LINE.match(line)
            if m:
                key = m.group(1).strip()
                value = parse_numeric(m.group(2))
                target = ensure_path(parsed, current_section, current_subsection)
                target[key] = value
                continue

        if artifacts:
            parsed["artifacts"] = artifacts

        return parsed

    def process(self, apollo_manager: ApolloManager) -> None:
        """
        Analyze batch of bitcode files in one version

        :param ApolloManager apollo_manager: Apollo manager
        """
        self.check_json_dir(apollo_manager)
        if not apollo_manager.bc_dir.exists():
            logger.error(f"wllvm_bc folder not found in {apollo_manager.apollo_root}")
            return
        # Using Bitcode Parser to check bitcode files
        bc_names = BitcodeParser.get_bitcode_names(apollo_manager)
        for bc_name in bc_names:
            stdout: Optional[str] = self.get_result(apollo_manager, bc_name)
            self.to_json(apollo_manager, bc_name, stdout)
