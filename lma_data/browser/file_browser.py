from typing import Iterator, TypeVar, Generic, Callable, Optional
from lma_data.browser.filters.filter import BrowserFilter
import glob, os

T = TypeVar("T")


def default_mapper(path: str) -> str:
    return path


class FileBrowser(Generic[T]):
    def __init__(self, mapper: Callable[[str], Optional[T]] = default_mapper):
        self._filters: list[BrowserFilter[T]] = []
        self._mapper = mapper
        self.glob_pathname = "**/*.*"

    def add_filter(self, browser_filter: BrowserFilter):
        self._filters.append(browser_filter)

    def ifind(self, root_dir: str, **kwargs) -> Iterator[T]:
        pathname = self._get_glob_pathname(root_dir)
        for path in glob.iglob(pathname, recursive=True):
            file = self._mapper(path)
            if file and self._test_file(path, file, **kwargs):
                yield file

    def find(self, root_dir: str, **kwargs) -> list[T]:
        pathname = self._get_glob_pathname(root_dir)
        files = []

        for path in glob.glob(pathname, recursive=True):
            file = self._mapper(path)
            if file and self._test_file(path, file, **kwargs):
                files.append(file)

        return files

    def _test_file(self, path: str, file: T, **kwargs):
        return all(map(lambda filter: filter.test(path, file, kwargs), self._filters))

    def _get_glob_pathname(self, root_dir: str) -> str:
        pathname = os.path.join(root_dir, self.glob_pathname)
        return pathname
