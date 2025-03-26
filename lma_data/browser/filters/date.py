from lma_data.browser.filters.filter import BrowserFilter
from datetime import datetime
from typing import Any, Callable, Optional, TypeVar
from lma_data.LMA_cli import parse_date_string
from lma_data.LMA_util import datetime_within
import argparse

T = TypeVar("T")


class DateFilter(BrowserFilter[T]):
    def __init__(self, date_parser: Callable[[str, T], Optional[datetime]]):
        self.start_date_arg_name = "start_date"
        self.end_date_arg_name = "end_date"
        self.date_parser = date_parser
        self.missing_date_accepted = False
        super().__init__(self._predicate)

    def _predicate(self, path: str, file: T, args: dict[str, Any]):
        path_datetime = self.date_parser(path, file)
        if not path_datetime:
            return self.missing_date_accepted

        start_date_str = args.get(self.start_date_arg_name)
        end_date_str = args.get(self.end_date_arg_name)
        start_date = parse_date_string(start_date_str)
        end_date = parse_date_string(end_date_str)

        return datetime_within(path_datetime, start_date, end_date)

    def add_parser_args(self, parser: argparse.ArgumentParser):
        parser.add_argument("--start-date", dest=self.start_date_arg_name, type=str)
        parser.add_argument("--end-date", dest=self.end_date_arg_name, type=str)
