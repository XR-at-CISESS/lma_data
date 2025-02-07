from setuptools import setup, find_packages

setup(
    name="lma_data",
    description="Scripts to transform and produce plots of LMA data",
    version="1.0",
    scripts=["lma-download", "lma-flash", "lma-plot", "lma-storm"],
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
