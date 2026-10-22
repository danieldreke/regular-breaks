#!/usr/bin/env python3
"""Install Regular Breaks: checks dependencies and adds an app-menu launcher.

Run from the repo directory: python3 install.py
"""
import os
import stat
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPT_PATH = os.path.join(SCRIPT_DIR, "regular_breaks.py")
ICON_PATH = os.path.join(SCRIPT_DIR, "icons", "coffee-cup.svg")

APPLICATIONS_DIR = os.path.join(os.path.expanduser("~"), ".local", "share", "applications")
DESKTOP_PATH = os.path.join(APPLICATIONS_DIR, "regular-breaks.desktop")


def check_dependencies():
    try:
        import gi
    except ImportError:
        print("Missing dependency: PyGObject (the 'gi' module).")
        print("On Debian/Ubuntu, install it with:")
        print("    sudo apt install python3-gi")
        return False

    try:
        gi.require_version("Gtk", "3.0")
        gi.require_version("AyatanaAppIndicator3", "0.1")
        from gi.repository import Gtk, AyatanaAppIndicator3  # noqa: F401
    except (ValueError, ImportError):
        print("Missing dependency: the AyatanaAppIndicator3 GObject introspection bindings.")
        print("On Debian/Ubuntu, install it with:")
        print("    sudo apt install gir1.2-ayatanaappindicator3-0.1")
        return False

    return True


def install_desktop_launcher():
    os.makedirs(APPLICATIONS_DIR, exist_ok=True)
    entry = (
        "[Desktop Entry]\n"
        "Type=Application\n"
        "Name=Regular Breaks\n"
        "Comment=Reminds you to take regular breaks and micro-pauses\n"
        f"Exec={sys.executable} {SCRIPT_PATH}\n"
        f"Icon={ICON_PATH}\n"
        "Terminal=false\n"
        "Categories=Utility;\n"
    )
    with open(DESKTOP_PATH, "w") as f:
        f.write(entry)
    print(f"Installed app-menu launcher: {DESKTOP_PATH}")


def main():
    if not sys.platform.startswith("linux"):
        print("Regular Breaks only supports Linux (GTK3 + Ayatana AppIndicator).")
        sys.exit(1)

    if not check_dependencies():
        sys.exit(1)

    os.chmod(SCRIPT_PATH, os.stat(SCRIPT_PATH).st_mode | stat.S_IEXEC)
    install_desktop_launcher()

    print()
    print("Install complete.")
    print(f"Run it directly with: {sys.executable} {SCRIPT_PATH}")
    print("Or find 'Regular Breaks' in your application menu.")
    print("Use the tray icon's 'Start on login' menu item to enable autostart.")


if __name__ == "__main__":
    main()
