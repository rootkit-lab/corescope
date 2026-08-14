"""Memory forensics: a thin wrapper around the Volatility3 `vol` CLI.

This module never talks to the Volatility3 Python framework/plugin API directly — it shells
out to the `vol` executable and captures its output, same as an analyst would from a
terminal. That keeps the wrapper honest about what it actually verified: the exact command
run is the evidence (see PLAN.md Section 5 and skill/corescope/SKILL.md).

Requires the optional `memory` extra (`pip install "corescope[memory]"`), which installs
volatility3 and its `vol` entry point.
"""

from __future__ import annotations

import shutil
import subprocess
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

VOL_BIN = "vol"

# Plugin used to probe whether a dump matches a given OS, and the default triage sequence
# run for that OS once detected. See skill/corescope/references/memory-forensics/.
OS_PROBE_PLUGIN = {
    "windows": "windows.info",
    "linux": "linux.info",
}

DEFAULT_TRIAGE_PLUGINS = {
    "windows": ["windows.pslist", "windows.psscan"],
    "linux": ["linux.pslist", "linux.psaux"],
}

Runner = Callable[[list[str]], subprocess.CompletedProcess]


class VolatilityNotAvailableError(RuntimeError):
    """Raised when the `vol` CLI (volatility3) is not installed/available on PATH."""


@dataclass
class PluginResult:
    plugin: str
    command: list[str]
    returncode: int
    stdout: str
    stderr: str

    @property
    def ok(self) -> bool:
        return self.returncode == 0

    def to_dict(self) -> dict:
        return {
            "plugin": self.plugin,
            "command": self.command,
            "returncode": self.returncode,
            "stdout": self.stdout,
            "stderr": self.stderr,
        }


@dataclass
class TriageResult:
    dump: str
    detected_os: str | None
    plugin_results: list[PluginResult] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "dump": self.dump,
            "detected_os": self.detected_os,
            "plugin_results": [r.to_dict() for r in self.plugin_results],
        }


def _default_runner(command: list[str]) -> subprocess.CompletedProcess:
    if shutil.which(command[0]) is None:
        raise VolatilityNotAvailableError(
            f"'{command[0]}' not found on PATH. Install the optional memory forensics "
            'extra first: pip install "corescope[memory]"'
        )
    return subprocess.run(command, capture_output=True, text=True, timeout=300)


def run_plugin(
    dump_path: str | Path,
    plugin: str,
    extra_args: list[str] | None = None,
    runner: Runner = _default_runner,
) -> PluginResult:
    """Run a single Volatility3 plugin against a dump. `plugin` must be a full name,
    e.g. "windows.pslist" — this wrapper does not guess or validate plugin names."""
    dump_path = Path(dump_path)
    if not dump_path.is_file():
        raise FileNotFoundError(dump_path)

    command = [VOL_BIN, "-f", str(dump_path), plugin, *(extra_args or [])]
    completed = runner(command)
    return PluginResult(
        plugin=plugin,
        command=command,
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )


def detect_os(dump_path: str | Path, runner: Runner = _default_runner) -> str | None:
    """Best-effort OS detection: try each OS's `.info` plugin, return the first that
    succeeds. Returns None if none of them do (unsupported/corrupt/unknown image)."""
    for os_name, plugin in OS_PROBE_PLUGIN.items():
        result = run_plugin(dump_path, plugin, runner=runner)
        if result.ok:
            return os_name
    return None


def triage(dump_path: str | Path, runner: Runner = _default_runner) -> TriageResult:
    """Detect the OS, then run the default triage plugin sequence for it. See
    skill/corescope/references/patterns/triage-checklist.md for the manual version of
    this same sequence and why each plugin is there (e.g. pslist+psscan, not just pslist)."""
    dump_path = Path(dump_path)
    if not dump_path.is_file():
        raise FileNotFoundError(dump_path)

    detected_os = detect_os(dump_path, runner=runner)
    result = TriageResult(dump=str(dump_path), detected_os=detected_os)

    if detected_os is None:
        return result

    for plugin in DEFAULT_TRIAGE_PLUGINS[detected_os]:
        result.plugin_results.append(run_plugin(dump_path, plugin, runner=runner))

    return result
