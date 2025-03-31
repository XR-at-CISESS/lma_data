from typing import TypeVar, Callable, Generic, Optional, Any
from lma_data.browser.filters.options import OptionsFilter
from lma_data.browser.filters.date import DateFilter
from lma_data.browser.filters.filter import BrowserFilter
from lma_data.browser.file_browser import FileBrowser
from lma_data.browser.filters.cache import CacheFilter
from datetime import datetime
from argparse import ArgumentParser


T = TypeVar("T")
U = TypeVar("U")
C = TypeVar("C")


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
    def create_cache_filter_from_browser(
        cache_browser: FileBrowser[U],
        get_file_cache_property: Callable[[str, T], C],
        get_cache_file_cache_property: Callable[[str, U], C],
        get_root_dir: Callable[[dict[str, Any]], str],
        **kw_args,
    ) -> CacheFilter[T]:
        def get_cache(args):
            root_dir = get_root_dir(args)
            for file, path in cache_browser.ifind2(root_dir, **kw_args):
                cache_val = get_cache_file_cache_property(path, file)
                yield cache_val

        cache_filter = CacheFilter(get_file_cache_property, get_cache)
        return cache_filter

    @staticmethod
    def apply_filters_to_argparser(parser: ArgumentParser, *filters: BrowserFilter[T]):
        for filter in filters:
            filter.apply_to_argparser(parser)

    @staticmethod
    def add_filters_to_browser(browser: FileBrowser, *filters: BrowserFilter[T]):
        for filter in filters:
            browser.add_filter(filter)
