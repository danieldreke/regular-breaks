#!/usr/bin/env python3
"""Download (and optionally install) Regular Breaks without needing git.

    curl -fsSL https://raw.githubusercontent.com/danieldreke/regular-breaks/main/download.py | python3 -
    curl -fsSL https://raw.githubusercontent.com/danieldreke/regular-breaks/main/download.py | python3 - --install
    curl -fsSL https://raw.githubusercontent.com/danieldreke/regular-breaks/main/download.py | python3 - --update
"""
import argparse
import io
import os
import subprocess
import sys
import tarfile
import urllib.request

REPO = "danieldreke/regular-breaks"


def fetch_tarball(ref):
    url = f"https://github.com/{REPO}/archive/refs/heads/{ref}.tar.gz"
    print(f"Downloading {url} ...")
    req = urllib.request.Request(url, headers={"User-Agent": "regular-breaks-downloader"})
    with urllib.request.urlopen(req) as response:
        return response.read()


def extract(data, dest):
    dest_abs = os.path.abspath(dest)
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tar:
        members = tar.getmembers()
        if not members:
            raise ValueError("downloaded archive is empty")
        # Archive root is "<repo>-<ref>/...", e.g. "regular-breaks-main/" -- strip it.
        prefix = members[0].name.split("/")[0] + "/"
        for member in members:
            if not member.name.startswith(prefix):
                continue
            rel_path = member.name[len(prefix):]
            if not rel_path:
                continue
            target = os.path.abspath(os.path.join(dest_abs, rel_path))
            if not target.startswith(dest_abs + os.sep):
                raise ValueError(f"unsafe path in archive: {member.name}")
            member.name = rel_path
            tar.extract(member, path=dest_abs)


def main():
    parser = argparse.ArgumentParser(description="Download Regular Breaks")
    parser.add_argument(
        "--dir", default="regular-breaks",
        help="target directory to download into (default: regular-breaks)",
    )
    parser.add_argument(
        "--ref", default="main",
        help="branch or tag to download (default: main)",
    )
    parser.add_argument(
        "--install", action="store_true",
        help="run install.py in the downloaded directory afterwards",
    )
    parser.add_argument(
        "--update", action="store_true",
        help="overwrite an existing --dir with the latest files instead of erroring",
    )
    args = parser.parse_args()

    dest = os.path.abspath(args.dir)
    if os.path.exists(dest) and os.listdir(dest) and not args.update:
        print(f"Error: {dest} already exists and is not empty.", file=sys.stderr)
        print("Remove it, pass --dir to choose a different location, or pass --update to overwrite.", file=sys.stderr)
        sys.exit(1)
    os.makedirs(dest, exist_ok=True)

    data = fetch_tarball(args.ref)
    extract(data, dest)
    print(f"{'Updated' if args.update else 'Downloaded to'} {dest}/")

    if args.install:
        print("Running install.py ...")
        result = subprocess.run([sys.executable, "install.py"], cwd=dest)
        sys.exit(result.returncode)

    print(f"Run it with:     {sys.executable} {os.path.join(dest, 'regular_breaks.py')}")
    print(f"Or install with: {sys.executable} {os.path.join(dest, 'install.py')}")


if __name__ == "__main__":
    main()
