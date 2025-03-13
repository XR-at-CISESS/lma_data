from datetime import datetime
from typing import Optional

def parse_date_string(date_str: Optional[str]) -> Optional[datetime]:
    """
    Attempts to parse a date string from a CLI argument.
    """
    if not date_str:
        return None
    
    try:
        return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        return None

def flatten_arg_values(arg_values: Optional[list[str]]) -> Optional[list[str]]:
    """
    Given multiple comma-separated append arguments (ex: -f a,b -f c), flatten
    them into a single value list (ex: ['a', 'b', 'c'])
    """
    if not arg_values:
        return None

    return [
        arg_value
        for arg_comma_values in arg_values
        for arg_value in arg_comma_values.split(",")
    ]
