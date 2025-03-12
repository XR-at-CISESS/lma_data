import argparse
from datetime import datetime
from lma_data.LMA_browser import LMABrowser
from lma_data.LMA_data_file import LMADataFile
from lma_data.LMA_cli import parse_date_string
from typing import Optional
from rich.table import Table
from rich.console import Console


def create_parser():
    parser = argparse.ArgumentParser(
        prog="lma_find", description="Helps locate LMA data files."
    )

    parser.add_argument("data_dir")
    parser.add_argument("-sd", "--start-date", dest="start_date")
    parser.add_argument("-ed", "--end-date", dest="end_date")
    parser.add_argument("-d", "--date", dest="date")
    parser.add_argument("-n", "--networks", dest="networks", action="append")
    parser.add_argument("-s", "--stations", action="append", dest="stations")
    parser.add_argument(
        "-g", "--group", dest="group_files", action="store_true", default=False
    )
    parser.add_argument(
        "-p",
        "--pretty",
        dest="pretty",
        action="store_true",
        help="Display discovered data files in a pretty/human-readable format.",
        default=False,
    )

    return parser


def find_files(
    data_dir: str,
    networks: Optional[list[str]],
    stations: Optional[list[str]],
    start_date: Optional[datetime],
    end_date: Optional[datetime],
) -> list[LMADataFile]:
    browser = LMABrowser()
    browser.find(data_dir)
    data_files = browser.query(
        network_ids=networks,
        station_ids=stations,
        start_date=start_date,
        end_date=end_date,
    )

    return data_files


def print_table(data_files: list[LMADataFile], group_files: bool):
    console = Console()
    table = Table(show_header=True, header_style="bold yellow")
    table.add_column("Date")
    table.add_column("Network")
    table.add_column("Station Name")
    table.add_column("Station Identifier")
    table.add_column("Path")

    last_date_time = None
    for data_file in data_files:
        date = str(data_file.datetime)
        if group_files and last_date_time != data_file.datetime:
            table.add_section()
            last_date_time = data_file.datetime
        elif group_files:
            date = "."

        table.add_row(
            date,
            data_file.network,
            data_file.station_name,
            data_file.station_identifier,
            data_file.path,
        )

    console.print(table)


def print_paths(data_files: list[LMADataFile], group_files: bool):
    last_date_time = None
    path_group = []
    def print_path_group():
        if not path_group:
            return
        
        print(",".join(path_group))
        
    for data_file in data_files:
        if group_files:
            if last_date_time != data_file.datetime:
                print_path_group()
                last_date_time = data_file.datetime
                path_group = [data_file.path]
            else:
                 path_group.append(data_file.path)
        else:
            print(data_file.path)
    
    if group_files:
        print_path_group()


def print_results(data_files: list[LMADataFile], group_files: bool, pretty: bool):
    if pretty:
        print_table(data_files, group_files)
    else:
        print_paths(data_files, group_files)


def flatten_arg_values(arg_values: Optional[list[str]]) -> Optional[list[str]]:
    if not arg_values:
        return None

    return [
        arg_value
        for arg_comma_values in arg_values
        for arg_value in arg_comma_values.split(",")
    ]


def main():
    parser = create_parser()
    args = parser.parse_args()
    data_dir = args.data_dir
    pretty = args.pretty
    stations = flatten_arg_values(args.stations)
    networks = flatten_arg_values(args.networks)
    start_date = parse_date_string(args.start_date)
    end_date = parse_date_string(args.end_date)
    date = parse_date_string(args.date)
    if date and (start_date or end_date):
        parser.error(
            "An exact date cannot be simultaneously specified with a start/end date."
        )
    elif date:
        start_date = date
        end_date = date

    group_files = args.group_files

    data_files = find_files(
        data_dir,
        networks=networks,
        stations=stations,
        start_date=start_date,
        end_date=end_date,
    )
    print_results(data_files, group_files, pretty)


if __name__ == "__main__":
    main()
