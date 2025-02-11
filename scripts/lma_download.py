#!/usr/bin/env python3
from subprocess import call
import os, sys
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


def main():
    network = sys.argv[1]
    year = sys.argv[2]
    month = sys.argv[3]
    days = sys.argv[4:]

    download_day(network, year, month, days)


if __name__ == "__main__":
    main()
