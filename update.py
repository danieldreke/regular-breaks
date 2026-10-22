#!/usr/bin/env python3
"""Update the Regular Breaks files in this folder.

    ./update.py
"""
import os
import sys

import download


def main():
    folder = os.path.dirname(os.path.abspath(__file__))
    if os.path.basename(folder) != download.PROJECT_NAME:
        print(
            f"Error: update.py must live in a folder named {download.PROJECT_NAME}.",
            file=sys.stderr,
        )
        sys.exit(1)
    # This script is already loaded, so replacing update.py on disk is safe.
    download.download_into(folder)
    print(f"Updated {folder}/")
    print("Quit the tray app and start it again so it runs the new code.")


if __name__ == "__main__":
    main()
