from lma_data.browser.filters.filter import BrowserFilter
from datetime import datetime
from typing import Any, TypeVar

T = TypeVar("T")


class CompoundFilter(BrowserFilter[T]):
    def __init__(self, filters: list[BrowserFilter]):
        self._filters = filters
        super().__init__(self._predicate)

    def _predicate(self, path: str, file: T, args: dict[str, Any]):
        return all(map(lambda filter: filter.test(path, args), self._filters))
