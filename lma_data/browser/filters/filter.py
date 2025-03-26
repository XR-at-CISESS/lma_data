from typing import Callable, Any, TypeVar, Generic

T = TypeVar("T")


class BrowserFilter(Generic[T]):
    def __init__(self, predicate: Callable[[str, T, dict[str, Any]], bool]):
        self.predicate = predicate

    def test(self, path: str, file: T, args: dict[str, Any]) -> bool:
        return self.predicate(path, file, args)
