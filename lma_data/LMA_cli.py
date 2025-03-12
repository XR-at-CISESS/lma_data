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
