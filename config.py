"""
module config: configuration for the project
"""
from pathlib import Path
import re

PROJECT_ROOT = Path(__file__).parent.absolute()

# =================== Modules list to be analyzed ==================
MODULES = ['audio', 'calibration', 'canbus', 'common', 'control', 'dreamview',
           'drivers', 'guardian', 'localization', 'map', 'monitor',
           'perception', 'planning', 'prediction', 'routing', 'storytelling',
           'tools', 'transform', 'v2x']
# ================================================================

# =================== Saber stdout parse pattern ==================
SECTION_LINE = re.compile(r"^\*{3,}\s*(.*?)\s*\*{3,}\s*$")
PROGRAM_LINE = re.compile(r"^#+\s*\(program\s*:\s*([0-9a-fA-F]+)\)\s*#+\s*$")
SUBSECTION_LINE = re.compile(r"^-{3,}\s*(.*?)\s*-{3,}\s*$")
WRITING_LINE = re.compile(r"^Writing\s+\'([^']+)\'\.\.\.$")
KEY_VALUE_LINE = re.compile(r"^([A-Za-z][A-Za-z0-9/ ]*?[A-Za-z0-9/])\s+(-?\d+(?:\.\d+)?)\s*$")
# ================================================================

# =================== Logging configuration ======================
_LOGGER_NAME = "AVIR"
"""Default logger name for the project"""
_SUCCESS_LEVEL_NUM = 25  # between INFO(20) and WARNING(30)
"""Success info level number for the project"""
# ================================================================
