from typing import Callable, Any, TypeVar
from argparse import ArgumentParser
from lma_data.browser.filters.filter import BrowserFilter
from lma_data.LMA_cli import flatten_arg_values

T = TypeVar("T")


class OptionsFilter(BrowserFilter[T]):
    def __init__(self, options_arg_name: str, get_property: Callable[[str, T], str]):
        self.options_arg_name = options_arg_name
        self.get_property = get_property
        self.case_insensitive = True
        super().__init__(self._predicate)

    def _predicate(self, path: str, file: T, args: dict[str, Any]):
        options = args.get(self.options_arg_name)
        if not options:
            return True

        options: list[str] = flatten_arg_values(options)
        val = self.get_property(path, file)

        if self.case_insensitive:
            options = [option.lower() for option in options]
            val = val.lower()

        return val in options

    def apply_to_argparser(self, parser: ArgumentParser, aliases: list[str] = []):
        parser.add_argument(
            f"--{self.options_arg_name}",
            *aliases,
            action="append",
            dest=self.options_arg_name,
        )
