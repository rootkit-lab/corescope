from pathlib import Path

import pytest

from corescope.binary.analyze import UnsupportedFormatError
from corescope.re.disassemble import DisassemblyError, disassemble_entrypoint

REAL_ELF = Path("/bin/true")


@pytest.mark.skipif(not REAL_ELF.exists(), reason="/bin/true not present on this system")
def test_disassemble_real_elf_entrypoint():
    result = disassemble_entrypoint(REAL_ELF)

    assert result.format == "elf"
    assert result.arch == "x86-64"
    assert result.entry_point > 0
    assert result.instructions, "expected at least one disassembled instruction"
    assert any("e_entry" in line for line in result.evidence)

    first = result.instructions[0]
    assert first.address == result.entry_point
    assert first.mnemonic
    assert len(first.bytes_hex) > 0


def test_disassemble_missing_file_raises_file_not_found(tmp_path):
    with pytest.raises(FileNotFoundError):
        disassemble_entrypoint(tmp_path / "does-not-exist")


def test_disassemble_non_binary_raises_unsupported_format(tmp_path):
    text_file = tmp_path / "readme.txt"
    text_file.write_text("hello")
    with pytest.raises(UnsupportedFormatError):
        disassemble_entrypoint(text_file)


def test_disassemble_truncated_elf_raises_disassembly_error(tmp_path):
    truncated = tmp_path / "truncated.elf"
    truncated.write_bytes(b"\x7fELF" + b"\x00" * 12)
    with pytest.raises(DisassemblyError):
        disassemble_entrypoint(truncated)


@pytest.mark.skipif(not REAL_ELF.exists(), reason="/bin/true not present on this system")
def test_disassemble_result_to_dict_round_trips_key_fields():
    result = disassemble_entrypoint(REAL_ELF, length=32)
    payload = result.to_dict()
    assert payload["format"] == "elf"
    assert payload["arch"] == "x86-64"
    assert isinstance(payload["instructions"], list)
    assert payload["instructions"][0]["mnemonic"] == result.instructions[0].mnemonic
