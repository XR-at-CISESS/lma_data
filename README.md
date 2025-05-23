# lma_data
Code used/developed while interning at the University of Maryland Earth System Science Interdisciplinary Center (ESSIC)

The goal of this project is to collect and process data of the three Lightning Mapping Array: DCLMA, WFFLMA, and MALMA and to analyze Mid-Atlantic Lightning Mapping Array (MALMA) multi-band network performance. The project uses Python and is partially built upon [lmatools](https://github.com/deeplycloudy/lmatools).

Since `lmatools` is not yet an official pip package, you first need to install it directly from its Git repository. If not, you can skip this step.

```
pip3 install git+https://github.com/XR-at-CISESS/lmatools.git 
```

Then, you can install `lma_data`:

```
pip3 install git+https://github.com/XR-at-CISESS/lma_data.git
```

## Commands

Once you install `lma_data`, several commands for processing LMA data will become available.

- `lma_batch`: Enables the simultaneous processing of several LMA data files at once. 

## Files

* **LMA_flash_sort_and_grid.py**
  * Modified version from [lmatools](https://github.com/deeplycloudy/lmatools) to cluster and grid LMA data files
* **LMA_storm_sort_and_grid.py**
  * Modified version of LMA_flash_sort_and_grid.py to sum LMA data within 24 hours 
* **LMA_source_plot_cartopy.py**
  * Plot gridded files produced by LMA_flash_sort_and_grid.py and LMA_storm_sort_and_grid.py
* **download_files.py**
  * Download LMA data files from ftp server (ftp://lma-tech.com/pub/)
* **LMA_info.py**
  * Contains coordinates of the three LMA networks
  
