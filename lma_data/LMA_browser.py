import glob, os
from lma_data.LMA_data_file import LMADataFile
from datetime import datetime
from typing import Optional
from lma_data.LMA_util import datetime_within


class LMABrowser:
    """
    Enables searching for and querying LMA data files
    """

    def __init__(self):
        self.data: dict[str, dict[str, list[LMADataFile]]] = {}

    def find(self, data_dir):
        """
        Finds all data files recursively within the specified directory and adds them to the browser.
        """

        data_paths = glob.glob(os.path.join(data_dir, "**/*.dat"), recursive=True)
        for data_path in data_paths:
            lma_file = LMADataFile.try_parse(data_path)
            if not lma_file:
                continue

            network = self.data.get(lma_file.network)
            if not network:
                network = self.data[lma_file.network] = {}

            station = network.get(lma_file.station_identifier)
            if not station:
                station = network[lma_file.station_identifier] = []

            station.append(lma_file)

        for network in self.data.values():
            for data_files in network.values():
                data_files.sort()

    def query(
        self,
        network_ids: list[str] = None,
        station_ids: list[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> list[LMADataFile]:
        queried_files: list[LMADataFile] = []
        network_ids = network_ids if network_ids else self.data.keys()

        for network_id in network_ids:
            network_id = network_id.lower()
            if not network_id in self.data:
                continue

            network = self.data[network_id]
            station_ids = station_ids if station_ids else network.keys()
            for station_id in station_ids:
                station_id = station_id.lower()
                if not station_id in network:
                    continue

                station_files = network[station_id]

                for data_file in station_files:
                    if datetime_within(data_file.datetime, start_date, end_date):
                        queried_files.append(data_file)  

        queried_files.sort()

        return queried_files

    def batch(
        self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None
    ) -> list[list[LMADataFile]]:
        batches = {}
        for network in self.data.values():
            for station in network.values():
                for data_file in station:
                    if datetime_within(data_file.datetime, start_date, end_date):
                        batch = batches.get(data_file.datetime)
                        if not data_file.datetime in batches:
                            batch = batches[data_file.datetime] = []

                        batch.append(data_file)

        sorted_batches = [
            batches[batch_datetime] for batch_datetime in sorted(batches.keys())
        ]

        return sorted_batches

    def get_station_data_files(self, network_identifier: str, station_identifier: str):
        network = self.data.get(network_identifier)
        if not network:
            return None

        return network.get(station_identifier)

    def clear(self):
        self.data = {}
