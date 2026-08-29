"""
module wrapper.svf: wrapper for SVF framework
"""
from typing import Optional, Dict
from pathlib import Path
from wrapper.analyzer import AnalyzerContainer
from wrapper.apollo import ApolloManager
from wrapper.parse import BitcodeParser

class SVFManager:
    """
    A wrapper for SVF framework to analyze the bitcode files using static analysis.

    Acknowledgment:

    - Yulei Sui and Jingling Xue. 2016.
      SVF: interprocedural static value-flow analysis in LLVM.
      In Proceedings of the 25th International Conference on Compiler Construction (CC '16).
      Association for Computing Machinery, New York, NY, USA, 265–266.
    - DOI: https://doi.org/10.1145/2892208.2892235
    - GitHub: https://github.com/SVF-tools/SVF
    """
    analyzer: AnalyzerContainer
    svf_dir: str
    tools: Dict[str, Path]
    parser: BitcodeParser

    def __init__(self, analyzer: AnalyzerContainer) -> None:
        """
        Constructor

        :param AnalyzerContainer analyzer: docker container avir-dev
        """
        self.analyzer = analyzer
        if not analyzer.is_running():
            if not analyzer.has_image():
                analyzer.build()
            analyzer.start()
        self.svf_dir = analyzer.svf_dir
        """the path of the SVF source code in the docker container from avir image"""
        self.tools = {
            'ae': Path(self.svf_dir) / "Release-build" / "bin" / "ae",
            'cfl': Path(self.svf_dir) / "Release-build" / "bin" / "cfl",
            'dvf': Path(self.svf_dir) / "Release-build" / "bin" / "dvf",
            'llvm2svf': Path(self.svf_dir) / "Release-build" / "bin" / "llvm2svf",
            'mta': Path(self.svf_dir) / "Release-build" / "bin" / "mta",
            'saber': Path(self.svf_dir) / "Release-build" / "bin" / "saber",
            'svf-ex': Path(self.svf_dir) / "Release-build" / "bin" / "svf-ex",
            'wpa': Path(self.svf_dir) / "Release-build" / "bin" / "wpa",
        }
        self.parser = BitcodeParser(analyzer)

    def analyze(self, tool: str, apollo_manager: ApolloManager, bc_name: str) -> Optional[str]:
        """
        Analyze the bitcode file using the specified tool

        :param str tool: the tool to use for analysis
        :param ApolloManager apollo_manager: Apollo manager
        :param str bc_name: Bitcode hash name
        :returns: the stdout of the analysis result
        :rtype: Optional[str]
        """
        bc_dir_in_ctn, _ = self.parser.get_path(apollo_manager, bc_name)
        if tool not in self.tools.keys():
            raise ValueError(f"Invalid tool: {tool}")
        tool_path = str(self.tools[tool])
        """the path of the tool in the analyzer container, should be str for exec in the container"""
        returncode, stdout, stderr = self.analyzer.exec([
            tool_path,
            str(bc_dir_in_ctn),
        ])
        if returncode != 0:
            raise RuntimeError(f"Failed to analyze bitcode: {bc_name} using {tool}")
        return stdout if stdout else None
