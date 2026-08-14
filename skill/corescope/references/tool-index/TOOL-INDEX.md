# Tool index — task to tool

| Task | Tool | Notes |
|---|---|---|
| Parse ELF headers/sections programmatically | `pyelftools` | Pure Python, no native deps |
| Parse PE headers/imports/exports programmatically | `pefile` | Pure Python |
| Cross-format (ELF/PE/Mach-O) parsing, one API | `LIEF` | Also does binary rewriting/patching |
| Disassemble instructions from raw bytes | `capstone` | Disassembly only, no container-format parsing |
| Pattern-match / IOC scan across files | `yara-python` | See `references/binary-analysis/strings-iocs-yara.md` |
| Deobfuscate stack strings / decoded-at-runtime strings | FLARE `floss` | Emulates relevant code, not just a static regex |
| Memory dump (RAM image) analysis | `volatility3` (`vol`) | See `references/memory-forensics/` |
| Detect packing signatures | Detect It Easy (DIE), `binwalk` | DIE for PE/ELF signatures+entropy, binwalk for embedded/appended data |
| Unpack UPX specifically | `upx -d` | Fails gracefully if header was tampered with |
| CFG recovery / symbolic execution | `angr` | `auto_load_libs=False` for single-sample triage |
| Lightweight CPU emulation of a code snippet | `unicorn` | You model memory/registers/hooks yourself |
| Interactive RE, free, has a decompiler | Ghidra (`analyzeHeadless` for scripting) | Jython by default; Ghidrathon for real CPython |
| Interactive RE, CLI-first, scriptable | radare2 / `r2pipe` | Steep initial learning curve, very scriptable |
| Extract embedded/appended files, firmware images | `binwalk` | Also useful for carving from memory dumps |
| Hashing for chain of custody | `sha256sum` (stdlib `hashlib` in Python) | Always hash before first analysis touch |

See `references/tool-index/GREP-RECIPES.md` for canned CLI one-liners, and the routing
table in `SKILL.md` for which `references/` file covers each domain in depth.
