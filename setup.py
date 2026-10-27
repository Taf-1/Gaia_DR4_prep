from setuptools import setup, find_packages

setup(
    name="gaia_dr4",
    version="0.1.0",
    description="Gaia DR4 Data Retrieval and Simulation",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Tafadzwa Zivave",
    author_email="tafadzwazivave@gmail.com"
    licence="MIT",
    packages=find_packages(exclude=["tests", "data", "logs"]),
    package_dir={"": "src"},
    install_requires=[
        "numpy",
        "pandas",
        "matplotlib",
        "astropy",
        "astroquery",
        "scipy",
        "tqdm",
        "pyarrow<15"
    ],
    entry_points={
        "console_scripts": [
            "gaia_dr4=main:main"
        ]
    },
    python_requires=">=3.8",
    include_package_data=True,
    classifiers=[
        "Programming Language <IP_ADDRESS> Python <IP_ADDRESS> 3",
        "License <IP_ADDRESS> OSI Approved <IP_ADDRESS> MIT License",
        "Operating System <IP_ADDRESS> OS Independent",
    ],
)