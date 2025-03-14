import argparse, subprocess, os, signal, shlex
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional
from lma_data.LMA_data_file import LMADataFile
from lma_data.LMA_browser import LMABrowser
from lma_data.LMA_cli import parse_date_string
from rich.progress import Progress
from threading import Event, Lock

lma_processes: list[subprocess.Popen[str]] = []
lma_process_lock = Lock()
lma_shutdown_event = Event()


def process_batch(batch: list[LMADataFile], lma_analysis_args: str, silent_mode: bool):
    if len(batch) == 0:
        return

    lma_datetime = batch[0].datetime
    date = lma_datetime.strftime("%Y%m%d")
    time = lma_datetime.strftime("%H%M%S")
    data_files = " ".join([data_file.path for data_file in batch])
    cmd = f"lma_analysis -d {date} -t {time} {lma_analysis_args} {data_files}"
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
                    lambda batch: process_batch(batch, lma_analysis_args, silent_mode),
                    batch,
                )
                for batch in batches
            ]

            # Wait for process to complete and update progress bar
            done = 0
            task = lma_progress.add_task("Processing LMA Data...")
            for _ in as_completed(futures):
                done += 1
                lma_progress.update(task, completed=float(done) / len(futures))


def create_parser():
    parser = argparse.ArgumentParser(
        prog="lma_batch",
        description="Quickly process multiple LMA files using lma_analysis",
    )
    parser.add_argument("data_dir")
    parser.add_argument("-sd", "--start_date", dest="start_date")
    parser.add_argument("-ed", "--end_date", dest="end_date")
    parser.add_argument(dest="lma_analysis_args", nargs=argparse.REMAINDER, default="")
    parser.add_argument("-n", "--num_workers", type=int, dest="num_workers")
    parser.add_argument("--silent", "-s", action="store_true", dest="silent_mode")
    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()
    browser = LMABrowser()
    browser.find(args.data_dir)

    start = parse_date_string(args.start_date)
    end = parse_date_string(args.end_date)
    num_workers = args.num_workers
    silent_mode = args.silent_mode

    batches = browser.batch(start, end)
    lma_analysis_args = " ".join(args.lma_analysis_args)
    process_batches(batches, lma_analysis_args, silent_mode, num_workers)


if __name__ == "__main__":
    main()
