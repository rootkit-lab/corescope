from pathlib import Path

import pytest

from corescope.binary.analyze import (
    AnalysisError,
    UnsupportedFormatError,
    analyze,
    detect_format,
    shannon_entropy,
)

REAL_ELF = Path("/bin/true")


def test_shannon_entropy_of_empty_is_zero():
    assert shannon_entropy(b"") == 0.0


def test_shannon_entropy_of_constant_bytes_is_zero():
    assert shannon_entropy(b"\x00" * 1000) == 0.0


def test_shannon_entropy_of_uniform_random_is_near_max():
    data = bytes(range(256)) * 16
    assert shannon_entropy(data) > 7.9


def test_detect_format_elf():
    assert detect_format(REAL_ELF) == "elf"


def test_detect_format_rejects_unknown(tmp_path):
    bogus = tmp_path / "not-a-binary.txt"
    bogus.write_bytes(b"just some plain text, not a binary at all")
    with pytest.raises(UnsupportedFormatError):
        detect_format(bogus)


@pytest.mark.skipif(not REAL_ELF.exists(), reason="/bin/true not present on this system")
def test_analyze_real_elf_has_sections_and_evidence():
    result = analyze(REAL_ELF)
    assert result.format == "elf"
    assert len(result.sha256) == 64
    assert result.sections, "expected at least one ELF section"
    assert any("ELF header" in line for line in result.evidence)
    assert any("sha256sum" in line for line in result.evidence)


def test_analyze_missing_file_raises_file_not_found(tmp_path):
    with pytest.raises(FileNotFoundError):
        analyze(tmp_path / "does-not-exist")


def test_analyze_non_binary_raises_unsupported_format(tmp_path):
    text_file = tmp_path / "readme.txt"
    text_file.write_text("hello")
    with pytest.raises(UnsupportedFormatError):
        analyze(text_file)


def test_analyze_truncated_elf_raises_analysis_error(tmp_path):
    truncated = tmp_path / "truncated.elf"
    # Real ELF magic, but nowhere near a valid header/section table -> parser must reject
    # this cleanly instead of the CLI crashing with an unhandled traceback.
    truncated.write_bytes(b"\x7fELF" + b"\x00" * 12)
    with pytest.raises(AnalysisError):
        analyze(truncated)


def test_analysis_result_to_dict_round_trips_key_fields():
    result = analyze(REAL_ELF)
    payload = result.to_dict()
    assert payload["format"] == "elf"
    assert payload["sha256"] == result.sha256
    assert isinstance(payload["sections"], list)
    assert isinstance(payload["imports"], list)
