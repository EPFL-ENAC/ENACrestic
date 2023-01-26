"""
Everything to package enacrestic

Based on:
+ https://packaging.python.org/tutorials/packaging-projects/
+ https://github.com/pypa/sampleproject

Build it with:
$ python3 -m build

This is automated with:
$ make package
"""

import pathlib
import re

from dynaconf import Dynaconf
from setuptools import setup

here = pathlib.Path(__file__).parent.resolve()
pyproject_meta = Dynaconf(
    settings_files=[here / "pyproject.toml"],
)

# ["Samuel Bancal <Samuel.Bancal@epfl.ch>"]
author, author_email = map(
    lambda s: s.strip(),
    re.search(
        r"^([^<]+)<([^>]+)>$", pyproject_meta.get("tool.poetry.authors")[0]
    ).groups(),
)

install_requires = list(
    filter(lambda dep: dep != "python", pyproject_meta.get("tool.poetry.dependencies"))
)

setup(
    name=pyproject_meta.get("tool.poetry.name"),
    version=pyproject_meta.get("tool.poetry.version"),
    description=pyproject_meta.get("tool.poetry.description"),
    long_description=(here / "README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    url=pyproject_meta.get("tool.poetry.homepage"),
    author=author,
    author_email=author_email,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "Environment :: X11 Applications :: Qt",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: POSIX :: Linux",
        "Topic :: System :: Archiving :: Backup",
    ],
    keywords="backup, restic",
    package_dir={"": "."},
    packages=["enacrestic"],
    python_requires=">=3.6, <4",
    install_requires=install_requires,
    extras_require={
        "dev": [],
        "test": [],
    },
    package_data={
        "enacrestic": ["pixmaps/*.png"],
    },
    data_files=[
        ("share/applications", ["enacrestic.desktop"]),
        ("share/icons", ["enacrestic.png"]),
    ],
    entry_points={
        "console_scripts": [
            "enacrestic=enacrestic:main.main",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/EPFL-ENAC/ENACrestic/issues",
        "Source": "https://github.com/EPFL-ENAC/ENACrestic/",
    },
)
