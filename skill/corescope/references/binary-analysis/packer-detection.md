# Packer / obfuscation detection

## Signals (combine several — no single one is conclusive)

1. **High entropy** in a code-like section. Shannon entropy near the theoretical max
   (~7.9-8.0 bits/byte) in what should be executable code suggests compressed/encrypted
   content unpacked at runtime. Legitimate compiled code is usually well below that
   (structured instruction patterns are not random).

   ```python
   import math
   from collections import Counter


   def shannon_entropy(data: bytes) -> float:
       if not data:
           return 0.0
       counts = Counter(data)
       length = len(data)
       return -sum((n / length) * math.log2(n / length) for n in counts.values())
   ```

2. **Tiny import table.** A PE that imports almost nothing besides `LoadLibraryA` /
   `GetProcAddress` (sometimes `VirtualAlloc`/`VirtualProtect`) is very likely resolving its
   real imports itself at runtime, after unpacking — a classic packer stub pattern.
3. **Section names/count look wrong for the compiler.** `UPX0`/`UPX1` sections are literally
   named after UPX. A "normal" MSVC/GCC binary with only 1-2 sections, or with an entry point
   outside `.text`, is suspicious.
4. **Near-zero hits from `strings`/YARA** on an otherwise substantial binary — see
   `strings-iocs-yara.md`. Real functionality has to reference *something* (API names,
   error messages, format strings) unless it's hidden behind packing.

## Tools

- `file` — sometimes recognizes known packer signatures directly.
- **Detect It Easy (DIE)** — signature database + entropy view, actively maintained, good
  first stop.
- **PEiD** — historical, signature-based, Windows-only; many signatures are stale now but
  still occasionally useful for older samples.
- `binwalk` — scans for embedded/appended files and known magic bytes (useful for firmware
  and for packers that append a compressed payload after the PE).

## UPX specifically

UPX is extremely common (used by both legitimate software and malware) and, unless the
header was deliberately corrupted to block this, is often directly reversible:

```bash
upx -d packed.exe -o unpacked.exe
```

If `upx -d` fails, the header was likely modified to resist that exact command while the
compression format is still UPX — manual unpacking (run to the OEP under a debugger, dump,
fix imports) is the fallback; see
`references/reverse-engineering/disassembly-decompilation.md`.

## After confirming packing

Packing is a **signal that static analysis of this file alone is incomplete**, not proof of
malicious intent (commercial software packs/obfuscates for IP protection too). Next step is
usually dynamic analysis in the sandbox to capture the unpacked code from memory — see
`references/reverse-engineering/` and the root `Dockerfile`.
