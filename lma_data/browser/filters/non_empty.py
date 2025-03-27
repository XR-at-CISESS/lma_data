from typing import Callable, Any, TypeVar
from argparse import ArgumentParser
from lma_data.browser.filters.filter import BrowserFilter
from lma_data.LMA_cli import flatten_arg_values
import os

T = TypeVar("T")


class NonEmptyFileFilter(BrowserFilter[T]):
    def __init__(self, st_size=2048):
        self.st_size = st_size
        super().__init__(self._predicate)

    def _predicate(self, path: str, file: T, args: dict[str, Any]):
        return os.stat(path).st_size >= self.st_size
