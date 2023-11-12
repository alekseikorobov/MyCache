import re
from pathlib import Path

from setuptools import setup

# p = Path(__file__).with_name("my_cache")/ "__init__.py"
# try:
#     version = re.findall(r"^__version__ = \"([^']+)\"\r?$", p.read_text(), re.M)[0]
# except IndexError:
#     raise RuntimeError("Unable to determine version.")

# readme = Path(__file__).with_name("README.rst").read_text()


setup(
    name="my_cache",
    version="0.0.1",
    author="aleksei korobov",
    url="https://github.com/alekseikorobov/mycache",
    author_email="",
    description="",
    long_description='readme',
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    packages=("my_cache",),
    install_requires=None,
    extras_require={
        "aiofiles": ["aiofiles>=23.2.1"],
        "aiojobs": ["aiojobs>=1.2.0"]
    },
    include_package_data=True,
)