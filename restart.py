#!/usr/bin/env python3
"""Stop Regular Breaks if it is running, then start it again.

    ./restart.py
"""
import os
import signal
import subprocess
import sys
import time

FOLDER = os.path.dirname(os.path.abspath(__file__))
APP = os.path.join(FOLDER, "regular_breaks.py")


def app_pids():
    found = []
    for entry in os.listdir("/proc"):
        if not entry.isdigit():
            continue
        pid = int(entry)
        if pid == os.getpid():
            continue
        try:
            raw = open(f"/proc/{pid}/cmdline", "rb").read().split(b"\x00")
            cwd = os.readlink(f"/proc/{pid}/cwd")
        except OSError:
            continue
        for arg in raw:
            if not arg:
                continue
            name = arg.decode()
            if os.path.basename(name) != "regular_breaks.py":
                continue
            path = name if os.path.isabs(name) else os.path.join(cwd, name)
            if os.path.abspath(path) == APP:
                found.append(pid)
                break
    return found


def stop_running():
    pids = app_pids()
    if not pids:
        return
    for pid in pids:
        os.kill(pid, signal.SIGTERM)
    deadline = time.time() + 5
    while time.time() < deadline and app_pids():
        time.sleep(0.1)
    for pid in app_pids():
        os.kill(pid, signal.SIGKILL)


def main():
    stop_running()
    subprocess.Popen(
        [sys.executable, APP],
        cwd=FOLDER,
        start_new_session=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    print("Restarted Regular Breaks.")


if __name__ == "__main__":
    main()
