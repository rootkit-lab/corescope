"""Static ELF/PE analysis: format detection, headers, sections, imports, entropy.

Every result carries the evidence (what was actually inspected) alongside the data —
see PLAN.md Section 5 and skill/corescope/SKILL.md ("verify empirically, then answer").
"""

from __future__ import annotations

import hashlib
import math
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

ELF_MAGIC = b"\x7fELF"
PE_MAGIC = b"MZ"


class UnsupportedFormatError(ValueError):
    """Raised when the file is not a recognized ELF or PE binary."""


class AnalysisError(RuntimeError):
    """Raised when the file matches a known magic but the parser rejects it (malformed)."""


@dataclass
class SectionInfo:
    name: str
    address: int
    size: int
    entropy: float


@dataclass
class AnalysisResult:
    path: str
    sha256: str
    format: str
    evidence: list[str] = field(default_factory=list)
    sections: list[SectionInfo] = field(default_factory=list)
    imports: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "sha256": self.sha256,
            "format": self.format,
            "evidence": self.evidence,
            "sections": [vars(s) for s in self.sections],
            "imports": self.imports,
        }


def shannon_entropy(data: bytes) -> float:
    """Bits per byte, 0.0 (empty/constant) to 8.0 (uniformly random)."""
    if not data:
        return 0.0
    counts = Counter(data)
    length = len(data)
    return -sum((n / length) * math.log2(n / length) for n in counts.values())


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def detect_format(path: Path) -> str:
    with path.open("rb") as f:
        header = f.read(4)
    if header[:4] == ELF_MAGIC:
        return "elf"
    if header[:2] == PE_MAGIC:
        return "pe"
    raise UnsupportedFormatError(f"{path}: not an ELF or PE file (magic bytes {header!r})")


def analyze(path: str | Path) -> AnalysisResult:
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(path)

    digest = sha256_of(path)
    fmt = detect_format(path)

    result = AnalysisResult(path=str(path), sha256=digest, format=fmt)
    result.evidence.append(f"sha256sum {path} -> {digest}")

    try:
        if fmt == "elf":
            _analyze_elf(path, result)
        else:
            _analyze_pe(path, result)
    except UnsupportedFormatError:
        raise
    except Exception as exc:  # noqa: BLE001 - normalize any parser-internal failure
        raise AnalysisError(f"{path}: failed to parse as {fmt.upper()}: {exc}") from exc

    return result


def _decode(value: bytes | str | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode(errors="replace")
    return str(value)


def _analyze_elf(path: Path, result: AnalysisResult) -> None:
    from elftools.elf.elffile import ELFFile

    with path.open("rb") as f:
        elf = ELFFile(f)
        result.evidence.append(
            f"ELF header: e_type={elf.header['e_type']} e_machine={elf.header['e_machine']}"
        )
        for section in elf.iter_sections():
            result.sections.append(
                SectionInfo(
                    name=section.name or "(unnamed)",
                    address=section["sh_addr"],
                    size=section["sh_size"],
                    entropy=round(shannon_entropy(section.data()), 3),
                )
            )
        dynsym = elf.get_section_by_name(".dynsym")
        if dynsym is not None:
            result.imports = sorted({sym.name for sym in dynsym.iter_symbols() if sym.name})


def _analyze_pe(path: Path, result: AnalysisResult) -> None:
    import pefile

    pe = pefile.PE(str(path))
    result.evidence.append(
        f"PE header: Machine=0x{pe.FILE_HEADER.Machine:x} "
        f"EntryPoint=0x{pe.OPTIONAL_HEADER.AddressOfEntryPoint:x}"
    )
    for section in pe.sections:
        result.sections.append(
            SectionInfo(
                name=_decode(section.Name).rstrip("\x00"),
                address=section.VirtualAddress,
                size=section.Misc_VirtualSize,
                entropy=round(shannon_entropy(section.get_data()), 3),
            )
        )
    imports: list[str] = []
    for entry in getattr(pe, "DIRECTORY_ENTRY_IMPORT", []):
        for imp in entry.imports:
            name = _decode(imp.name)
            if name:
                imports.append(name)
    result.imports = sorted(set(imports))
