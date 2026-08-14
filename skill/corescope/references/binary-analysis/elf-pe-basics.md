# ELF / PE basics

Identify the format before picking a tool: `file <path>` first, always — it reads the
magic bytes for you and is nearly instant.

## ELF (Linux/Unix)

- Magic: `7f 45 4c 46` (`\x7fELF`) at offset 0.
- `e_type` tells you a lot immediately: `ET_EXEC` (classic non-PIE executable), `ET_DYN`
  (either a shared library **or** a modern PIE executable — check for an entry point +
  `.interp` to disambiguate), `ET_REL` (unlinked object file), `ET_CORE` (core dump, e.g.
  from `windows.memmap --dump` on Linux or `gcore`).
- Program headers (`PT_LOAD`, etc.) describe what the **loader** maps at runtime — this is
  what matters for execution/RE. Section headers (`.text`, `.data`, `SHT_SYMTAB`, ...) are
  for the **linker/debugger** and can be fully stripped without affecting execution.
- `.dynamic` + `.interp` present → dynamically linked (depends on `ld-linux.so` +
  shared libs, check with `ldd` or `readelf -d`). Absent → statically linked.
- Stripped (`strip` was run, or compiled with `-s`): no `.symtab`, function names gone from
  `nm`/`objdump -t`. `file` output omits "not stripped" in that case. Structure, strings,
  and control flow are still fully analyzable — a stripped binary is harder, not opaque.

```python
from elftools.elf.elffile import ELFFile

with open(path, "rb") as f:
    elf = ELFFile(f)
    print(elf.header["e_type"], elf.header["e_machine"])
    for section in elf.iter_sections():
        print(section.name, hex(section["sh_addr"]), section["sh_size"])
```

## PE (Windows)

- Magic: `MZ` (DOS stub header) at offset 0; the real PE signature (`PE\0\0`) lives at the
  offset stored in `e_lfanew` inside that DOS header.
- Sections are conventionally named `.text` (code), `.data`/`.rdata` (data/read-only data),
  `.rsrc` (resources — icons, version info, sometimes embedded payloads), but names are
  cosmetic; a packer can rename/merge them arbitrarily.
- **Import Address Table (IAT)**: which external functions the binary calls — often the
  fastest capability triage (`CreateRemoteThread`+`WriteProcessMemory` → injection;
  `WinExec`/`ShellExecute` → spawns processes; `InternetOpen`/`WinHttp*` → network).
  A tiny import table (just `LoadLibraryA`/`GetProcAddress`) is a strong packing signal —
  see `packer-detection.md`.
- **Export table**: relevant for DLLs — what other modules can call into it.

```python
import pefile

pe = pefile.PE(path)
for entry in pe.DIRECTORY_ENTRY_IMPORT:
    for imp in entry.imports:
        print(entry.dll, imp.name)
```

## Cross-format: LIEF

`LIEF` parses ELF/PE/Mach-O with one API — convenient when the format isn't known ahead of
time, or for quick cross-platform scripts:

```python
import lief

binary = lief.parse(path)
print(binary.format, binary.entrypoint)
```

## See also

- `references/binary-analysis/strings-iocs-yara.md`
- `references/binary-analysis/packer-detection.md`
- `references/tool-index/GREP-RECIPES.md` — `readelf`/`objdump` one-liners
