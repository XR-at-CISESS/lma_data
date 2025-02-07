import os


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
