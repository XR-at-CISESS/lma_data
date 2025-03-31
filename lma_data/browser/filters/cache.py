from lma_data.browser.filters.filter import BrowserFilter
from lma_data.browser.file_browser import FileBrowser
from datetime import datetime
from typing import Any, Callable, Iterable, TypeVar, Optional
import argparse

T = TypeVar("T")
C = TypeVar("C")


class CacheFilter(BrowserFilter[T]):
    def __init__(
        self,
        get_file_cache_property: Callable[[str, T], C],
        get_cache_items: Callable[[dict[str, Any]], Iterable[C]],
    ):
        self._get_file_cache_property = get_file_cache_property
        self._get_cache_items = get_cache_items
        self.no_cache_arg = "no_cache"
        self._cache: Optional[set[C]] = None
        super().__init__(self._predicate)

    def _predicate(self, path: str, file: T, args: dict[str, Any]):
        no_cache = args.get(self.no_cache_arg)
        if no_cache:
            return True

        if not self._cache:
            self._load_cache(args)

        key_val = self._get_file_cache_property(path, file)
        not_in_cache = not key_val in self._cache

        return not_in_cache

    def apply_to_argparser(self, parser: argparse.ArgumentParser):
        parser.add_argument(f"--no-cache", action="store_true")

    def _load_cache(self, args: dict[str, Any]):
        self._cache = set(self._get_cache_items(args))
