#!/usr/bin/env python3

import argparse

from enacrestic import __version__, app


def main():
    parser = argparse.ArgumentParser(
        prog="enacrestic", description="Automate restic execution"
    )
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument(
        "--no-gui",
        dest="gui",
        action="store_const",
        const=False,
        default=True,
        help="disable GUI integration (system tray ++)",
    )
    args = parser.parse_args()

    app.App(gui_enabled=args.gui)


if __name__ == "__main__":
    main()
