from subprocess import call
import os, argparse
from lma_data.LMA_util import get_lma_data_dir


def download_day(network, year, month, days=[]):
    data_dir = get_lma_data_dir()
    path = os.path.join(data_dir, f"{network}/data/{year}/{month}")

    for day in sorted(days):

        if network == "MALMA":
            ftp = f"ftp://lma-tech.com/pub/{network.lower()}/20{month}{day}/*.gz"
        else:
            ftp = f"ftp://lma-tech.com/pub/{network.lower()}_5sta/20{month}{day}/*.gz"

        outpath = f"{path}/{day}/"

        if os.path.exists(outpath) == False:
            os.makedirs(outpath)
        call(["wget", "-w", "2", ftp, "-P", outpath])


def create_parser():
    parser = argparse.ArgumentParser(
        prog="lma_download",
        description="Quickly process multiple LMA files using lma_analysis",
    )
    parser.add_argument("network")
    parser.add_argument("year")
    parser.add_argument("month")
    parser.add_argument("days", nargs=argparse.REMAINDER)
    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()

    network = args.network
    year = args.year
    month = args.month
    days = args.days

    download_day(network, year, month, days)


if __name__ == "__main__":
    main()
