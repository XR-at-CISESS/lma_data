from datetime import datetime
from typing import Optional
import argparse


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


def add_filter_args(parser: argparse.ArgumentParser):
    parser.add_argument(
        "-sd",
        "--start-date",
        dest="start_date",
        help="A start date before which data files are discarded. Cannot be simultaneously specified with an exact date.",
    )
    parser.add_argument(
        "-ed",
        "--end-date",
        dest="end_date",
        help="An end date after which data files are discarded. Cannot be simultaneously specified with an exact date.",
    )
    parser.add_argument(
        "-d",
        "--date",
        dest="date",
        help="An EXACT date to search for. Cannot be simultaneously specified with a start/end date.",
    )
    parser.add_argument(
        "-n",
        "--networks",
        dest="networks",
        action="append",
        help="A comma-separated filter for networks to include in the results",
    )
    parser.add_argument(
        "-s",
        "--stations",
        action="append",
        dest="stations",
        help="A comma-separated filter for stations to include in the results",
    )
