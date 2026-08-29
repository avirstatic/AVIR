"""
module framework: framework classes for different components
"""
from typing import Union, Dict, Optional

def parse_numeric(value: str) -> Union[float, int, str]:
    """
    Parse a numeric value from a string

    :param str value: the value to parse
    :returns: the parsed numeric value
    :rtype: Union[float, int, str]
    """
    if "." in value:
        try:
            return float(value)
        except ValueError:
            return value
    try:
        return int(value)
    except ValueError:
        return value

def ensure_path(obj: Dict, section: Optional[str], subsection: Optional[str]) -> Dict:
    """
    Ensure nested dict path exists: obj[section][subsection]

    :param Dict obj: the dictionary to ensure the path exists
    :param Optional[str] section: the section of the path
    :param Optional[str] subsection: the subsection of the path
    :returns: the dictionary with the path exists
    :rtype: Dict
    """
    if section is None:
        return obj
    if section not in obj or not isinstance(obj[section], dict):
        obj[section] = {}
    if subsection:
        if subsection not in obj[section] or not isinstance(obj[section][subsection], dict):
            obj[section][subsection] = {}
        return obj[section][subsection]
    return obj[section]
