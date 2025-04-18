import argparse, subprocess, os, signal, shlex
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional
from lma_data.LMA_data_file import LMADataFile
from lma_data.LMA_browser import LMABrowser
from lma_data.browser.file_browser import FileBrowser
from lma_data.LMA_filters import LMAFilters
from lma_data.LMA_util import batch
from lma_data.lma_analysis_data_file import LMAAnalysisDataFile
from rich.progress import Progress
from threading import Event, Lock

lma_processes: list[subprocess.Popen[str]] = []
lma_process_lock = Lock()
lma_shutdown_event = Event()


def process_batch(
    batch: list[LMADataFile],
    out_dir: str,
    lma_analysis_bin: str,
    lma_analysis_args: str,
    silent_mode: bool,
):
    if len(batch) == 0:
        return

    lma_datetime = batch[0].datetime
    date = lma_datetime.strftime("%Y%m%d")
    time = lma_datetime.strftime("%H%M%S")
    data_files = " ".join([data_file.path for data_file in batch])
    cmd = f"{lma_analysis_bin} -d {date} -t {time} -o {out_dir} {lma_analysis_args} {data_files}"
    cmd_args = shlex.split(cmd)

    # Attempt to create the process
    with lma_process_lock:
        if lma_shutdown_event.is_set():
            return

        lma_analysis_process = subprocess.Popen(
            cmd_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        lma_processes.append(lma_analysis_process)

    if not silent_mode:
        for line in lma_analysis_process.stdout:
            print(f"[{lma_datetime}] {line}", end="")

    lma_analysis_process.wait()

    with lma_process_lock:
        lma_processes.remove(lma_analysis_process)


def setup_signal_catcher():
    def on_exit(signum, frame):
        did_already_shutdown = lma_shutdown_event.is_set()
        if not did_already_shutdown:
            print("Terminating...")

        with lma_process_lock:
            lma_shutdown_event.set()

            for lma_process in lma_processes:
                if did_already_shutdown:
                    lma_process.kill()
                else:
                    lma_process.terminate()

    signal.signal(signal.SIGINT, on_exit)
    signal.signal(signal.SIGTERM, on_exit)


def process_batches(
    batches: list[list[LMADataFile]],
    out_dir: str,
    lma_analysis_bin: str,
    lma_analysis_args: str,
    silent_mode: bool = False,
    num_workers: Optional[int] = None,
):
    if not num_workers:
        num_workers = os.cpu_count()

    with Progress() as lma_progress:
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            setup_signal_catcher()

            futures = [
                executor.submit(
                    lambda batch: process_batch(
                        batch, out_dir, lma_analysis_bin, lma_analysis_args, silent_mode
                    ),
                    batch,
                )
                for batch in batches
            ]

            # Wait for process to complete and update progress bar
            done = 0
            task = lma_progress.add_task("Processing LMA Data...")
            for _ in as_completed(futures):
                done += 1
                lma_progress.update(task, completed=(100 * float(done) / len(futures)))


def create_parser():
    parser = argparse.ArgumentParser(
        prog="lma_batch",
        description="Quickly process multiple LMA files using lma_analysis",
    )

    parser.add_argument("data_dir")
    parser.add_argument("out_dir")
    parser.add_argument(dest="lma_analysis_args", nargs=argparse.REMAINDER, default="")

    parser.add_argument("-n", "--num_workers", type=int, dest="num_workers")
    parser.add_argument("--silent", "-s", action="store_true", dest="silent_mode")
    parser.add_argument(
        "-b",
        "--lma-analysis-bin",
        type=str,
        dest="lma_analysis_bin",
        help="The location of the lma_analysis binary",
        default="lma_analysis",
    )
    return parser


def create_cache_filter():
    cache_browser = FileBrowser(LMAAnalysisDataFile.try_parse)
    cache_filter = LMAFilters[LMADataFile].create_cache_filter_from_browser(
        cache_browser,
        lambda _, file: file.datetime,
        lambda _, file: file.datetime,
        lambda args: args["out_dir"],
    )

    return cache_filter


def main():
    parser = create_parser()

    date_filter = LMAFilters[LMADataFile].create_date_filter(
        lambda _, file: file.datetime
    )
    network_filter = LMAFilters[LMADataFile].create_network_filter(
        lambda _, file: file.network
    )
    station_filter = LMAFilters[LMADataFile].create_station_filter(
        lambda _, file: file.station_identifier
    )
    cache_filter = create_cache_filter()

    filters = [date_filter, network_filter, station_filter, cache_filter]

    LMAFilters.apply_filters_to_argparser(parser, *filters)
    args = parser.parse_args()

    browser = FileBrowser(LMADataFile.try_parse)
    LMAFilters.add_filters_to_browser(browser, *filters)
    data_files = browser.find(args.data_dir, **vars(args))

    num_workers = args.num_workers
    silent_mode = args.silent_mode
    out_dir = args.out_dir
    lma_analysis_bin = args.lma_analysis_bin

    batches = batch(data_files, lambda file: file.datetime)
    lma_analysis_args = " ".join(args.lma_analysis_args)
    process_batches(
        batches, out_dir, lma_analysis_bin, lma_analysis_args, silent_mode, num_workers
    )


if __name__ == "__main__":
    main()
