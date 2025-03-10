import re, os
from datetime import datetime
from typing import Optional, Self
from dataclasses import dataclass


@dataclass
class LMADataFile:
    """
    Parsing utilities for a LMA data file
    """

    LMA_FILE_NAME_RE = re.compile(r".*L([a-zA-Z]*)_([a-zA-Z]*)_(\w*)_(\d{6})_(\d{6})")

    def __init__(
        self,
        path: str,
        station_identifier: str,
        network: str,
        station_name: str,
        datetime: datetime,
    ):
        self.path = path
        self.station_identifier = station_identifier
        self.network = network
        self.station_name = station_name
        self.datetime = datetime

    @staticmethod
    def try_parse(data_path: str) -> Optional["LMADataFile"]:
        lma_match = LMADataFile.LMA_FILE_NAME_RE.match(data_path)
        if not lma_match:
            return None

        station_identifier, network, station_name, date, time = lma_match.groups()
        data_datetime = datetime.strptime(f"{date}T{time}", "%y%m%dT%H%M%S")
        lma_data_file = LMADataFile(
            data_path, station_identifier, network, station_name, data_datetime
        )

        return lma_data_file

    def __repr__(self):
        return f"LMADataFile({self.datetime} @ {self.station_name} [{self.network}/{self.station_identifier}])"

    def __lt__(self, other: Self):
        return (self.datetime, self.network, self.station_identifier) < (
            other.datetime,
            other.network,
            other.station_identifier,
        )

    def __eq__(self, other: Self):
        return (
            self.network == other.network
            and self.station_identifier == other.station_identifier
            and self.datetime == other.datetime
        )
