"""Tests for the Volatility3 `vol` wrapper.

None of these need a real memory dump or a real `vol` install: `run_plugin`/`detect_os`/
`triage` all accept an injected `runner`, so tests fake the subprocess call instead of
needing volatility3 (an optional, heavy extra not installed in the dev/CI environment).
"""

import shutil
import subprocess
from pathlib import Path

import pytest

from corescope.memory.analyze import (
    DEFAULT_TRIAGE_PLUGINS,
    VolatilityNotAvailableError,
    detect_os,
    run_plugin,
    triage,
)

# Any existing file works as a stand-in "dump" for tests that only exercise the
# file-existence check and never actually reach a real vol invocation.
EXISTING_FILE = Path("/bin/true") if Path("/bin/true").exists() else Path(__file__)


def _fake_runner(returncode: int, stdout: str = "", stderr: str = ""):
    def runner(command: list[str]) -> subprocess.CompletedProcess:
        return subprocess.CompletedProcess(
            args=command, returncode=returncode, stdout=stdout, stderr=stderr
        )

    return runner


def _os_aware_runner(succeeds_for: str):
    """Fake runner: succeeds only for commands whose plugin argument is `succeeds_for`."""

    def runner(command: list[str]) -> subprocess.CompletedProcess:
        plugin = command[3]
        ok = plugin == succeeds_for
        return subprocess.CompletedProcess(
            args=command,
            returncode=0 if ok else 1,
            stdout=f"output for {plugin}" if ok else "",
            stderr="" if ok else "plugin failed",
        )

    return runner


def test_run_plugin_missing_dump_raises_file_not_found(tmp_path):
    with pytest.raises(FileNotFoundError):
        run_plugin(tmp_path / "does-not-exist.raw", "windows.pslist", runner=_fake_runner(0))


def test_run_plugin_builds_expected_command_and_result():
    result = run_plugin(
        EXISTING_FILE, "windows.pslist", runner=_fake_runner(0, stdout="pid  name\n1  init")
    )
    assert result.command == ["vol", "-f", str(EXISTING_FILE), "windows.pslist"]
    assert result.plugin == "windows.pslist"
    assert result.ok is True
    assert "pid" in result.stdout


def test_run_plugin_with_extra_args_appends_them():
    result = run_plugin(
        EXISTING_FILE, "windows.pslist", extra_args=["--pid", "1234"], runner=_fake_runner(0)
    )
    assert result.command[-2:] == ["--pid", "1234"]


def test_run_plugin_nonzero_returncode_is_not_ok():
    result = run_plugin(EXISTING_FILE, "windows.info", runner=_fake_runner(1, stderr="boom"))
    assert result.ok is False
    assert result.stderr == "boom"


def test_detect_os_returns_matching_os():
    assert detect_os(EXISTING_FILE, runner=_os_aware_runner("linux.info")) == "linux"
    assert detect_os(EXISTING_FILE, runner=_os_aware_runner("windows.info")) == "windows"


def test_detect_os_returns_none_when_nothing_matches():
    assert detect_os(EXISTING_FILE, runner=_fake_runner(1)) is None


def test_triage_missing_dump_raises_file_not_found(tmp_path):
    with pytest.raises(FileNotFoundError):
        triage(tmp_path / "does-not-exist.raw", runner=_fake_runner(0))


def test_triage_runs_default_plugins_for_detected_os():
    result = triage(EXISTING_FILE, runner=_os_aware_runner("linux.info"))

    assert result.detected_os == "linux"
    ran_plugins = [r.plugin for r in result.plugin_results]
    assert ran_plugins == DEFAULT_TRIAGE_PLUGINS["linux"]
    # Only linux.info was configured to succeed; the triage plugins themselves are expected
    # to "fail" under this particular fake, which is fine — we're testing the sequencing.
    assert all(not r.ok for r in result.plugin_results)


def test_triage_unknown_os_runs_no_plugins():
    result = triage(EXISTING_FILE, runner=_fake_runner(1))
    assert result.detected_os is None
    assert result.plugin_results == []


@pytest.mark.skipif(shutil.which("vol") is not None, reason="vol is installed in this environment")
def test_default_runner_raises_when_vol_not_installed():
    # No `runner=` override: exercises the real default runner. `vol` is intentionally not
    # part of the core/dev dependency set (see pyproject.toml `memory` extra), so this should
    # reliably fail with a clear error rather than a raw subprocess/FileNotFoundError.
    with pytest.raises(VolatilityNotAvailableError):
        run_plugin(EXISTING_FILE, "windows.info")
