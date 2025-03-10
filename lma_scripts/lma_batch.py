import argparse, subprocess
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from lma_data.LMA_data_file import LMADataFile
from lma_data.LMA_browser import LMABrowser


def process_batch(batch: list[LMADataFile], lma_analysis_args: str):
    if len(batch) == 0:
        return
    
    lma_datetime = batch[0].datetime
    date = lma_datetime.strftime("%Y%m%d")
    time = lma_datetime.strftime("%H%M%S")
    duration = 300
    data_files = " ".join([data_file.path for data_file in batch])
    cmd = f"lma_analysis -d {date} -t {time} -s {duration} {lma_analysis_args} {data_files}"
    subprocess.run(cmd, shell=True)
    print(f"Done {lma_datetime}")

def process_batches(batches, lma_analysis_args: str):
    with ThreadPoolExecutor(max_workers=16) as executor:
        for batch in batches:
            executor.submit(process_batch, batch, lma_analysis_args)


def create_parser():
    parser = argparse.ArgumentParser(
        prog="lma_batch",
        description="Quickly process multiple LMA files using lma_analysis",
    )
    parser.add_argument("data_dir")
    parser.add_argument("start_date")
    parser.add_argument("end_date")
    parser.add_argument(
        dest="lma_analysis_args", nargs=argparse.REMAINDER, default=""
    )
    return parser


def parse_date_string(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        print(f"Invalid date format: {date_str}")
        exit(1)


def main():
    parser = create_parser()
    args = parser.parse_args()
    browser = LMABrowser()
    browser.find(args.data_dir)

    start = parse_date_string(args.start_date)
    end = parse_date_string(args.end_date)

    batches = browser.batch(start, end)
    lma_analysis_args = " ".join(args.lma_analysis_args)
    process_batches(batches, lma_analysis_args)


if __name__ == "__main__":
    main()
