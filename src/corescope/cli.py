"""Command-line entry point for corescope.

Kept thin on purpose: this module only parses arguments and dispatches to the
analysis packages (``corescope.memory``, ``corescope.binary``). No analysis
logic belongs here — see PLAN.md Section 5.
"""

from __future__ import annotations

import argparse
import json
import sys

from corescope import __version__
from corescope.binary.analyze import AnalysisError, UnsupportedFormatError, analyze
from corescope.memory.analyze import VolatilityNotAvailableError
from corescope.memory.analyze import run_plugin as mem_run_plugin
from corescope.memory.analyze import triage as mem_triage
from corescope.re.disassemble import (
    DEFAULT_LENGTH,
    DisassemblyError,
    UnsupportedArchitectureError,
    disassemble_entrypoint,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="corescope",
        description="Memory forensics, binary analysis, and reverse engineering toolkit.",
    )
    parser.add_argument("--version", action="version", version=f"corescope {__version__}")

    subparsers = parser.add_subparsers(dest="command")

    mem = subparsers.add_parser("mem", help="Memory forensics (Volatility3-backed).")
    mem.add_argument("dump", help="Path to a memory dump/image.")
    mem.add_argument(
        "--plugin",
        help="Run this exact Volatility3 plugin (e.g. windows.pslist). "
        "Default: auto-detect OS and run the default triage sequence.",
    )
    mem.add_argument("--json", action="store_true", help="Print machine-readable JSON.")

    binary = subparsers.add_parser("bin", help="Static binary analysis (ELF/PE).")
    binary.add_argument("path", help="Path to the binary/sample to inspect.")
    binary.add_argument("--json", action="store_true", help="Print machine-readable JSON.")

    re_parser = subparsers.add_parser("re", help="Reverse engineering helpers.")
    re_parser.add_argument("path", help="Path to the binary/sample to inspect.")
    re_parser.add_argument(
        "--length",
        type=int,
        default=DEFAULT_LENGTH,
        help=f"Bytes to disassemble from the entry point (default: {DEFAULT_LENGTH}).",
    )
    re_parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")

    return parser


def _run_bin(path: str, as_json: bool) -> int:
    try:
        result = analyze(path)
    except FileNotFoundError:
        print(f"corescope bin: no such file: {path}", file=sys.stderr)
        return 1
    except (UnsupportedFormatError, AnalysisError) as exc:
        print(f"corescope bin: {exc}", file=sys.stderr)
        return 1

    if as_json:
        print(json.dumps(result.to_dict(), indent=2))
        return 0

    print(f"{result.path}  ({result.format.upper()}, sha256={result.sha256})")
    for line in result.evidence:
        print(f"  evidence: {line}")
    print(f"  sections ({len(result.sections)}):")
    for section in result.sections:
        flag = "  <- high entropy" if section.entropy >= 7.0 else ""
        print(
            f"    {section.name:<16} addr=0x{section.address:<10x} "
            f"size={section.size:<10} entropy={section.entropy}{flag}"
        )
    if result.imports:
        shown = ", ".join(result.imports[:20])
        suffix = " ..." if len(result.imports) > 20 else ""
        print(f"  imports ({len(result.imports)}): {shown}{suffix}")
    return 0


def _run_mem(dump: str, plugin: str | None, as_json: bool) -> int:
    try:
        if plugin:
            result = mem_run_plugin(dump, plugin)
        else:
            result = mem_triage(dump)
    except FileNotFoundError:
        print(f"corescope mem: no such file: {dump}", file=sys.stderr)
        return 1
    except VolatilityNotAvailableError as exc:
        print(f"corescope mem: {exc}", file=sys.stderr)
        return 1

    if as_json:
        print(json.dumps(result.to_dict(), indent=2))
        return 0

    if plugin:
        print(f"{dump}  plugin={plugin}")
        print(f"  command: {' '.join(result.command)}")
        print(f"  returncode: {result.returncode}")
        print(result.stdout or "(no stdout)")
        if not result.ok:
            print(result.stderr, file=sys.stderr)
        return 0 if result.ok else 1

    print(f"{dump}  detected_os={result.detected_os or 'unknown'}")
    if result.detected_os is None:
        print("  could not detect OS (windows.info/linux.info both failed)", file=sys.stderr)
        return 1
    for plugin_result in result.plugin_results:
        print(f"  == {plugin_result.plugin} (returncode={plugin_result.returncode}) ==")
        print(plugin_result.stdout or "  (no stdout)")
    return 0


def _run_re(path: str, length: int, as_json: bool) -> int:
    try:
        result = disassemble_entrypoint(path, length=length)
    except FileNotFoundError:
        print(f"corescope re: no such file: {path}", file=sys.stderr)
        return 1
    except (UnsupportedFormatError, UnsupportedArchitectureError, DisassemblyError) as exc:
        print(f"corescope re: {exc}", file=sys.stderr)
        return 1

    if as_json:
        print(json.dumps(result.to_dict(), indent=2))
        return 0

    header = f"({result.format.upper()}, {result.arch}, entry=0x{result.entry_point:x})"
    print(f"{result.path}  {header}")
    for line in result.evidence:
        print(f"  evidence: {line}")
    for insn in result.instructions:
        print(f"  0x{insn.address:x}:  {insn.mnemonic} {insn.op_str}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 0

    if args.command == "bin":
        return _run_bin(args.path, args.json)
    if args.command == "mem":
        return _run_mem(args.dump, args.plugin, args.json)
    if args.command == "re":
        return _run_re(args.path, args.length, args.json)

    print(
        f"corescope {args.command}: not implemented yet — see ROADMAP.md Fase 2.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
