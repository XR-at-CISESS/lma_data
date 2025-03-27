from typing import TypeVar, Callable, Generic, Optional
from lma_data.browser.filters.options import OptionsFilter
from lma_data.browser.filters.date import DateFilter
from lma_data.browser.filters.filter import BrowserFilter
from lma_data.browser.file_browser import FileBrowser
from datetime import datetime
from argparse import ArgumentParser


T = TypeVar("T")


class LMAFilters(Generic[T]):
    @staticmethod
    def create_network_filter(get_property: Callable[[str, T], str]):
        network_filter = OptionsFilter[T]("network", get_property)
        return network_filter

    @staticmethod
    def create_station_filter(get_property: Callable[[str, T], str]):
        station_filter = OptionsFilter[T]("stations", get_property)
        return station_filter

    @staticmethod
    def create_date_filter(get_property: Callable[[str, T], Optional[datetime]]):
        date_filter = DateFilter[T](get_property)
        return date_filter

    @staticmethod
    def apply_filters_to_argparser(parser: ArgumentParser, *filters: BrowserFilter[T]):
        for filter in filters:
            filter.apply_to_argparser(parser)

    @staticmethod
    def add_filters_to_browser(browser: FileBrowser, *filters: BrowserFilter[T]):
        for filter in filters:
            browser.add_filter(filter)
