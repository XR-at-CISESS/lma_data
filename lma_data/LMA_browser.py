import glob, os
from lma_data.LMA_data_file import LMADataFile
from datetime import datetime


class LMABrowser:
    """
    Enables searching for and querying LMA data files
    """

    def __init__(self):
        self.lma_files: dict[str, dict[str, list[LMADataFile]]] = {}

    def find(self, data_dir):
        """
        Finds all data files recursively within the specified directory and adds them to the browser.
        """

        data_paths = glob.glob(os.path.join(data_dir, "**/*.dat"), recursive=True)
        for data_path in data_paths:
            lma_file = LMADataFile.try_parse(data_path)
            if lma_file:
                network = self.lma_files.get(lma_file.network)
                if not network:
                    network = self.lma_files[lma_file.network] = {}

                station = network.get(lma_file.station_identifier)
                if not station:
                    station = network[lma_file.station_identifier] = []

                station.append(lma_file)

        for network in self.lma_files.values():
            for data_files in network.values():
                data_files.sort()

    def batch(
        self, start_date: datetime, end_date: datetime
    ) -> list[list[LMADataFile]]:
        batches = {}
        for network in self.lma_files.values():
            for station in network.values():
                for data_file in station:
                    if (
                        start_date <= data_file.datetime
                        and data_file.datetime <= end_date
                    ):
                        batch = batches.get(data_file.datetime)
                        if not data_file.datetime in batches:
                            batch = batches[data_file.datetime] = []

                        batch.append(data_file)

        sorted_batches = [
            batches[batch_datetime] for batch_datetime in sorted(batches.keys())
        ]

        return sorted_batches

    def get_station_data_files(self, network_identifier: str, station_identifier: str):
        network = self.lma_files.get(network_identifier)
        if not network:
            return None

        return network.get(station_identifier)

    def clear(self):
        self.lma_files = {}
