"""Entry-point disassembly via capstone.

Static only: reads the entry point's code bytes straight from the container format
(ELF/PE) and disassembles them. No execution, no unpacking — see
skill/corescope/references/reverse-engineering/ for when a sample needs more than this
(emulation, symbolic execution, or a full interactive disassembler/decompiler).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from capstone import (
    CS_ARCH_ARM,
    CS_ARCH_ARM64,
    CS_ARCH_X86,
    CS_MODE_32,
    CS_MODE_64,
    CS_MODE_ARM,
    Cs,
)

from corescope.binary.analyze import detect_format

DEFAULT_LENGTH = 64


class UnsupportedArchitectureError(RuntimeError):
    """Raised when the binary's architecture has no known capstone mapping."""


class DisassemblyError(RuntimeError):
    """Raised when the entry point can't be resolved to actual code bytes."""


@dataclass
class Instruction:
    address: int
    mnemonic: str
    op_str: str
    bytes_hex: str


@dataclass
class DisassemblyResult:
    path: str
    format: str
    arch: str
    entry_point: int
    evidence: list[str] = field(default_factory=list)
    instructions: list[Instruction] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "format": self.format,
            "arch": self.arch,
            "entry_point": self.entry_point,
            "evidence": self.evidence,
            "instructions": [vars(i) for i in self.instructions],
        }


def disassemble_entrypoint(path: str | Path, length: int = DEFAULT_LENGTH) -> DisassemblyResult:
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(path)

    fmt = detect_format(path)  # raises UnsupportedFormatError, propagated as-is

    try:
        if fmt == "elf":
            return _disassemble_elf(path, length)
        return _disassemble_pe(path, length)
    except (UnsupportedArchitectureError, DisassemblyError):
        raise
    except Exception as exc:  # noqa: BLE001 - normalize parser-internal failures
        raise DisassemblyError(f"{path}: failed to disassemble as {fmt.upper()}: {exc}") from exc


def _run_capstone(
    cs_arch: int, cs_mode: int, code: bytes, base_address: int, result: DisassemblyResult
) -> None:
    md = Cs(cs_arch, cs_mode)
    for insn in md.disasm(code, base_address):
        result.instructions.append(
            Instruction(
                address=insn.address,
                mnemonic=insn.mnemonic,
                op_str=insn.op_str,
                bytes_hex=insn.bytes.hex(),
            )
        )
    result.evidence.append(
        f"capstone disassembled {len(result.instructions)} instruction(s) from "
        f"{len(code)} raw bytes"
    )


# name -> (label, capstone arch, capstone mode). CS_MODE_ARM == 0, which capstone also
# accepts as the mode for AArch64 (ARM64 has no separate meaningful mode flag).
_ELF_MACHINE_TO_CAPSTONE = {
    "EM_X86_64": ("x86-64", CS_ARCH_X86, CS_MODE_64),
    "EM_386": ("x86-32", CS_ARCH_X86, CS_MODE_32),
    "EM_AARCH64": ("arm64", CS_ARCH_ARM64, CS_MODE_ARM),
    "EM_ARM": ("arm", CS_ARCH_ARM, CS_MODE_ARM),
}

_PE_MACHINE_TO_CAPSTONE = {
    0x8664: ("x86-64", CS_ARCH_X86, CS_MODE_64),  # IMAGE_FILE_MACHINE_AMD64
    0x14C: ("x86-32", CS_ARCH_X86, CS_MODE_32),  # IMAGE_FILE_MACHINE_I386
    0xAA64: ("arm64", CS_ARCH_ARM64, CS_MODE_ARM),  # IMAGE_FILE_MACHINE_ARM64
}


def _disassemble_elf(path: Path, length: int) -> DisassemblyResult:
    from elftools.elf.elffile import ELFFile

    with path.open("rb") as f:
        elf = ELFFile(f)
        machine = elf.header["e_machine"]
        mapping = _ELF_MACHINE_TO_CAPSTONE.get(machine)
        if mapping is None:
            raise UnsupportedArchitectureError(f"unsupported ELF machine: {machine}")
        arch_label, cs_arch, cs_mode = mapping

        entry = elf.header["e_entry"]
        code = None
        for section in elf.iter_sections():
            addr = section["sh_addr"]
            size = section["sh_size"]
            if addr and addr <= entry < addr + size:
                data = section.data()
                offset = entry - addr
                code = data[offset : offset + length]
                break
        if code is None:
            raise DisassemblyError(f"entry point 0x{entry:x} not found in any ELF section")

    result = DisassemblyResult(path=str(path), format="elf", arch=arch_label, entry_point=entry)
    result.evidence.append(f"ELF e_entry=0x{entry:x} e_machine={machine}")
    _run_capstone(cs_arch, cs_mode, code, entry, result)
    return result


def _disassemble_pe(path: Path, length: int) -> DisassemblyResult:
    import pefile

    pe = pefile.PE(str(path))
    machine = pe.FILE_HEADER.Machine
    mapping = _PE_MACHINE_TO_CAPSTONE.get(machine)
    if mapping is None:
        raise UnsupportedArchitectureError(f"unsupported PE machine: 0x{machine:x}")
    arch_label, cs_arch, cs_mode = mapping

    entry_rva = pe.OPTIONAL_HEADER.AddressOfEntryPoint
    entry_va = pe.OPTIONAL_HEADER.ImageBase + entry_rva
    code = pe.get_data(entry_rva, length)

    result = DisassemblyResult(path=str(path), format="pe", arch=arch_label, entry_point=entry_va)
    result.evidence.append(
        f"PE AddressOfEntryPoint=0x{entry_rva:x} "
        f"ImageBase=0x{pe.OPTIONAL_HEADER.ImageBase:x} Machine=0x{machine:x}"
    )
    _run_capstone(cs_arch, cs_mode, code, entry_va, result)
    return result
