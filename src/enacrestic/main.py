#!/usr/bin/env python3

import argparse

from enacrestic import __version__, app


def main():
    parser = argparse.ArgumentParser(
        prog="enacrestic", description="Automate restic execution"
    )
    parser.add_argument("--version", action="version", version=__version__)
    parser.parse_args()

    app.main()


if __name__ == "__main__":
    main()
