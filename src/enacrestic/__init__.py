#!/usr/bin/env python3

import argparse
from enacrestic import app, const

def main():
    parser = argparse.ArgumentParser(
        prog='enacrestic',
        description='Automate restic execution'
    )
    parser.add_argument(
        '--version',
        action='version',
        version=const.VERSION
    )
    parser.parse_args()

    app.main()

if __name__ == '__main__':
    main()
