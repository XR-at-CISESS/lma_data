import re, os
from datetime import datetime
from typing import Optional, Self
from dataclasses import dataclass

LMA_ANALYSIS_DATA_FILE_RE = re.compile(r".*?\/?([a-zA-Z0-9]+)_(\d+)_(\d+)_(\d+)")


@dataclass
class LMAAnalysisDataFile:
    path: str
    network: str
    datetime: datetime

    @staticmethod
    def try_parse(path: str) -> Optional["LMAAnalysisDataFile"]:
        lma_match = LMA_ANALYSIS_DATA_FILE_RE.match(path)
        if not lma_match:
            return None

        network, date, time, misc = lma_match.groups()
        # Prepend 20 for 20XX dates
        data_datetime = datetime.strptime(f"20{date}T{time}", "%Y%m%dT%H%M%S")
        lma_data_file = LMAAnalysisDataFile(path, network, data_datetime)

        return lma_data_file
