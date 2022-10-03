#!/usr/bin/env python3

import argparse

from enacrestic import app

__version__ = "0.1.0"


def main():
    parser = argparse.ArgumentParser(
        prog="enacrestic", description="Automate restic execution"
    )
    parser.add_argument("--version", action="version", version=__version__)
    parser.parse_args()

    app.main()


if __name__ == "__main__":
    main()
