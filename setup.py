from setuptools import setup, find_packages

setup(
    name="lma_data",
    description="Scripts to transform and produce plots of LMA data",
    version="1.0",
    scripts=[
        "scripts/lma-download.py",
        "scripts/lma-flash.py",
        "scripts/lma-plot.py",
        "scripts/lma-storm.py",
    ],
    packages=find_packages(),
    install_requires=[
        "scikit-learn",
        "tables",
        "matplotlib",
        "pandas",
        "Cartopy",
        "netCDF4",
        "numpy",
        "scipy",
        "shapely",
    ],
)
