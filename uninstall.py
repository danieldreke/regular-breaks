#!/usr/bin/env python3
"""Uninstall Regular Breaks: removes the app-menu launcher and any autostart entry.

Leaves config.txt, icons/, and the repo itself untouched.
Run from the repo directory: python3 uninstall.py
"""
import os

APPLICATIONS_DIR = os.path.join(os.path.expanduser("~"), ".local", "share", "applications")
DESKTOP_PATH = os.path.join(APPLICATIONS_DIR, "regular-breaks.desktop")

AUTOSTART_DIR = os.path.join(os.path.expanduser("~"), ".config", "autostart")
AUTOSTART_DESKTOP_PATH = os.path.join(AUTOSTART_DIR, "regular-breaks.desktop")


def remove(path, description):
    if os.path.exists(path):
        os.remove(path)
        print(f"Removed {description}: {path}")
    else:
        print(f"No {description} found, nothing to do.")


def main():
    remove(DESKTOP_PATH, "app-menu launcher")
    remove(AUTOSTART_DESKTOP_PATH, "autostart entry")
    print()
    print("Uninstall complete. config.txt and icons/ were left in place.")


if __name__ == "__main__":
    main()
