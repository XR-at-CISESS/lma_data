import re, os
from datetime import datetime
from typing import Optional, Self
from dataclasses import dataclass

LMA_TOOLS_FILE_RE = re.compile(
    r".*?\/?([a-zA-Z0-9]+)_(\d+)_(\d+)_(\d+)_(\d+)src_([a-zA-Z0-9.]+)\-dx_(.*)"
)


@dataclass
class LMAToolsFile:
    """
    Parsing utilities for a LMA data file
    """

    path: str
    prefix: str
    datetime: datetime
    duration: int
    min_points_per_flash: int
    dx_units: str
    suffix: str

    @staticmethod
    def try_parse(path: str) -> Optional["LMAToolsFile"]:
        lma_match = LMA_TOOLS_FILE_RE.match(path)
        if not lma_match:
            return None

        prefix, date, time, duration, ppf, units, suffix = lma_match.groups()
        duration = int(duration)
        ppf = int(ppf)
        data_datetime = datetime.strptime(f"{date}T{time}", "%Y%m%dT%H%M%S")
        lma_data_file = LMAToolsFile(
            path, prefix, data_datetime, duration, ppf, units, suffix
        )

        return lma_data_file
