from setuptools import setup, find_packages

setup(
    name="lma_data",
    description="Scripts to transform and produce plots of LMA data",
    version="1.0",
    entry_points={
        "console_scripts": [
            "lma_download=lma_scripts.lma_download:main",
            "lma_flash=lma_scripts.lma_flash:main",
            "lma_plot=lma_scripts.lma_plot:main",
            "lma_storm=lma_scripts.lma_storm:main",
            "lma_batch=lma_scripts.lma_batch:main",
            "lma_find=lma_scripts.lma_find:main"
        ]
    },
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
        "lmatools",
        "rich"
    ],
)
