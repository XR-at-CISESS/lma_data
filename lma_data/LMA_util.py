import os, datetime
from typing import Optional

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

def datetime_within(datetime: datetime.datetime, start_date: Optional[datetime.datetime], end_date: Optional[datetime.datetime]):
    """
    Determines whether a datetime exists wtihin a start/end date, if they are
    specified.
    """
    if start_date and datetime < start_date:
        return False
    
    if end_date and datetime > end_date:
        return False

    return True