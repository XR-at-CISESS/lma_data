import os, datetime
from typing import Optional
from typing import TypeVar, Callable, Any


def get_lma_data_dir():
    """_summary_
    Get's the directory where LMA data is stored.

    Returns:
        str: The absolute path of the LMA directory.
    """
    lma_directory = os.environ.get("LMA_DATA_DIR", "./LMA_DATA")
    abs_path = os.path.abspath(lma_directory)

    return abs_path


def get_lma_out_dir():
    """_summary_
    Get's the directory where transformed LMA data is written to.

    Returns:
        str: The absolute path of the LMA directory.
    """
    lma_directory = os.environ.get("LMA_OUT_DIR", "./LMA_OUT")
    abs_path = os.path.abspath(lma_directory)

    return abs_path


def get_lma_shapes_dir():
    """_summary_
    Get's the directory where transformed LMA data is written to.

    Returns:
        str: The absolute path of the LMA directory.
    """
    shapes_directory = os.environ.get("LMA_SHAPES_DIR", ".")
    abs_path = os.path.abspath(shapes_directory)

    return abs_path


def datetime_within(
    datetime: datetime.datetime,
    start_date: Optional[datetime.datetime],
    end_date: Optional[datetime.datetime],
):
    """
    Determines whether a datetime exists wtihin a start/end date, if they are
    specified.
    """
    if start_date and datetime < start_date:
        return False

    if end_date and datetime > end_date:
        return False

    return True


T = TypeVar("T")


def batch(items: list[T], *batch_properties: Callable[[T], Any]):
    batches = []
    batch_map = {}
    for item in items:
        property_map = batch_map

        for i in range(len(batch_properties) - 1):
            batch_property = batch_properties[i]
            val = batch_property(item)
            if not val in property_map:
                property_map[val] = {}

            property_map = property_map[val]

        last_val = batch_properties[-1](item)
        if not last_val in property_map:
            property_map[last_val] = []

        batch: list[T] = property_map[last_val]
        batch.append(item)

    stack = [batch_map]
    while len(stack) > 0:
        item = stack.pop()
        if isinstance(item, dict):
            for val in item.values():
                stack.append(val)
        elif isinstance(item, list):
            batches.append(item)

    return batches
