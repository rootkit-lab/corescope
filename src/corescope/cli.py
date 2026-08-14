"""Command-line entry point for corescope.

Kept thin on purpose: this module only parses arguments and dispatches to the
analysis packages (``corescope.memory``, ``corescope.binary``). No analysis
logic belongs here — see PLAN.md Section 5.
"""

from __future__ import annotations

import argparse
import sys

from corescope import __version__


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="corescope",
        description="Memory forensics, binary analysis, and reverse engineering toolkit.",
    )
    parser.add_argument("--version", action="version", version=f"corescope {__version__}")

    subparsers = parser.add_subparsers(dest="command")

    mem = subparsers.add_parser("mem", help="Memory forensics (Volatility3-backed).")
    mem.add_argument("dump", help="Path to a memory dump/image.")

    binary = subparsers.add_parser("bin", help="Static binary analysis (ELF/PE).")
    binary.add_argument("path", help="Path to the binary/sample to inspect.")

    re_parser = subparsers.add_parser("re", help="Reverse engineering helpers.")
    re_parser.add_argument("path", help="Path to the binary/sample to inspect.")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 0

    print(
        f"corescope {args.command}: not implemented yet — see ROADMAP.md Fase 2.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
