# Strings, IOCs, and YARA

## Strings — mind the encoding

```bash
strings -a -n 8 sample.bin        # default: single-byte (ASCII/Latin-1) sequences, len >= 8
strings -a -e l -n 8 sample.bin   # UTF-16LE — most strings in Windows PE malware are here
```

Default `strings` only finds single-byte-encoded text. **Windows binaries very commonly
store strings as UTF-16LE** (Win32 `wchar_t`), which the default mode will not find at all
— see `references/pitfalls/what-doesnt-work.md`. Always run both encodings on a PE.

For strings that are obfuscated (stack strings, XOR'd, built char-by-char at runtime), plain
`strings` finds nothing — use FLARE's `floss` (`pip install flare-floss`), which emulates
the relevant code paths to recover them.

## IOC extraction

Simple regex triage over `strings` output — treat as **leads to verify, not facts**:

```python
import re

IP_RE = re.compile(rb"\b(?:\d{1,3}\.){3}\d{1,3}\b")
URL_RE = re.compile(rb"https?://[^\s\"'<>]+")
DOMAIN_RE = re.compile(rb"\b[a-z0-9-]+\.[a-z]{2,}\b", re.IGNORECASE)
```

Known false-positive sources: version strings (`4.5.6.7` matches the IP regex), compiler/
library metadata, legitimate CDN/telemetry URLs bundled by a benign framework. Cross-check
any hit against `windows.netscan` (if you have a matching memory dump) before calling it a
C2 address.

## YARA

Rule structure:

```
rule suspicious_stack_strings_and_section
{
    meta:
        author = "corescope"
        confidence = "medium"
    strings:
        $a = "cmd.exe /c" wide ascii
        $b = { E8 ?? ?? ?? ?? 83 C4 04 }   // hex byte pattern, ?? = wildcard nibble
    condition:
        $a and $b
}
```

`wide` matches UTF-16LE (pairs with the strings encoding note above). `ascii` matches the
default single-byte encoding — include both when you don't know which the sample uses.

```python
import yara

rules = yara.compile(filepath="rules.yar")
for match in rules.match(sample_path):
    print(match.rule, match.strings)
```

Write narrow rules (specific byte patterns / combined conditions) — a single short ASCII
string as the whole rule matches too much unrelated software and burns analyst time on
false positives.

## See also

- `references/binary-analysis/packer-detection.md` — packed samples yield almost nothing
  to strings/YARA until unpacked.
- `references/tool-index/TOOL-INDEX.md`
