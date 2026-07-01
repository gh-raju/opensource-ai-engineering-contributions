"""Covenant command-line interface."""
from __future__ import annotations

import argparse
from typing import Optional

from . import __version__


def main(argv: Optional[list] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="covenant",
        description="A pre-production trust harness for AI agents.",
    )
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("version", help="Print the installed version")
    sub.add_parser("demo", help="Run the bundled synthetic support-agent demo")

    args = parser.parse_args(argv)

    if args.command == "version":
        print(f"covenant {__version__}")
        return 0

    if args.command == "demo":
        from .demos.support_agent import run

        return run()

    parser.print_help()
    return 0
