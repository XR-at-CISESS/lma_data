from lma_data.browser.filters.filter import BrowserFilter
from typing import Any, TypeVar
import re

T = TypeVar("T")


class PathRegexFilter(BrowserFilter[T]):
    def __init__(self, re_pattern: str):
        self.pattern = re.compile(re_pattern)
        super().__init__(self._predicate)

    def _predicate(self, path: str, file: T, args: dict[str, Any]):
        return self.pattern.match(path) is not None
