from setuptools import setup, find_packages

setup(
    name="lma_data",
    description="Scripts to transform and produce plots of LMA data",
    version="1.0",
    entry_points={
        "console_scripts": [
            "lma-download=scripts.lma-download:main",
            "lma-flash=scripts.lma-flash:main",
            "lma-plot=scripts.lma-plot:main",
            "lma-storm=scripts.lma-storm:main"
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
        "lmatools"
    ],
)
