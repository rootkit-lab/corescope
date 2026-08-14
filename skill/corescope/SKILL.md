---
name: corescope
description: >
  Memory forensics, static binary analysis, and reverse engineering assistant backed by
  ranked, verifiable sources (Volatility3, pyelftools/pefile/LIEF, capstone, yara-python,
  angr/unicorn). Use for ANY task involving memory dump / RAM image triage, ELF or PE
  static analysis, malware/IOC triage, packer detection, disassembly, decompilation
  support, or reverse engineering of an unknown binary. Triggers on: "memory dump",
  "volatility", "RAM image", ".vmem", ".dmp", "reverse engineer this binary", "malware
  analysis", "ELF", "PE file", "disassemble", "decompile", "YARA rule", "IOC extraction",
  "packed binary", "unpack this". Always use this skill instead of answering from memory —
  it exists specifically so API/plugin/flag names are verified, not guessed.
---

# corescope — memory forensics, binary analysis, reverse engineering

**The defining rule of this skill: verify empirically, then answer.** Run the tool, quote
the command and its output (or the address/offset it points to), then draw the conclusion.
A signature/plugin/flag you have just run beats one you remember.

---

## Scope — ethical and legal use only

Only help analyze samples/systems the user owns or is explicitly authorized to examine
(their own lab, a CTF, an authorized incident-response engagement, academic research).

**Refuse and explain instead when asked to:**
- produce a functional malware payload, packer, or C2 for real-world unauthorized use
- weaponize a vulnerability against a system the user does not own/have authorization for
- help evade detection on a system that is not the user's own lab/sandbox

Analysis, detection engineering, and understanding *how* something works are always in
scope. Building a working weapon for unauthorized use is not.

**Any dynamic execution of an untrusted sample must happen inside the isolated sandbox**
(`Dockerfile` at repo root, `docker run --network=none ...`). Never suggest running an
unknown/untrusted binary directly on the host.

---

## Source precedence (highest first)

| Rank | Source | Grade | Notes |
|---|---|---|---|
| 1 | Run the real tool against the real sample/dump now | verified | `vol -f dump.raw windows.pslist`, `readelf -h`, `r2 -A`, etc. — cite the exact command + output |
| 2 | `references/` in this skill (curated, validated patterns) | validated-pattern | always available, offline |
| 3 | `corescope` CLI output (`corescope bin\|mem\|re`) | verified | thin wrapper, still counts as rank 1 if you actually ran it |
| 4 | Official docs via WebFetch (Volatility3 docs, pyelftools/LIEF docs) | doc | needs network; label the answer doc-grade |

Never invent a plugin name, CLI flag, or struct field. If none of the above resolves it,
say so explicitly and propose how to verify (e.g. "run `vol -h` to list available plugins
for this profile").

---

## Routing table

| Question | Go to |
|---|---|
| How do I triage a new memory dump? | `references/patterns/triage-checklist.md` |
| Volatility3 plugins, pslist vs psscan, malfind, acquisition | `references/memory-forensics/` |
| ELF/PE structure, sections, imports/exports | `references/binary-analysis/elf-pe-basics.md` |
| Extracting strings/IOCs, writing/running YARA | `references/binary-analysis/strings-iocs-yara.md` |
| Is this binary packed/obfuscated? | `references/binary-analysis/packer-detection.md` |
| Disassembly, decompilation, which tool to use | `references/reverse-engineering/disassembly-decompilation.md` |
| Emulation (`unicorn`), symbolic execution (`angr`) | `references/reverse-engineering/emulation-and-symbolic-execution.md` |
| Anti-debug / anti-VM tricks in the sample | `references/reverse-engineering/anti-analysis-tricks.md` |
| "I tried X and it didn't work" / known traps | `references/pitfalls/what-doesnt-work.md` ⭐ always check |
| Which tool/library should I use for task X? | `references/tool-index/TOOL-INDEX.md` |
| Canned grep/search recipes for a binary or corpus | `references/tool-index/GREP-RECIPES.md` |

---

## How to answer a corescope question

1. **Identify the domain** (memory / binary / RE) using the routing table above.
2. **Read the relevant reference** for the validated pattern.
3. **Run the real tool** against the real sample/dump — via the `corescope` CLI
   (`corescope mem|bin|re`, see below) or the underlying tool directly (`vol`, `r2`,
   `objdump`, `readelf`, `strings`).
4. **Check `references/pitfalls/what-doesnt-work.md`** before finalizing any conclusion —
   several intuitive-sounding claims in this domain are known traps.
5. **Cite the evidence**: exact command run + the relevant line(s) of output, or the
   address/offset. Never state a fact about the sample without it.

## The `corescope` CLI

```bash
corescope mem <dump>     # memory forensics (Volatility3-backed)
corescope bin <path>     # static ELF/PE analysis
corescope re  <path>     # reverse-engineering helpers
```

Install with `pip install -e .` (core) or `pip install -e ".[memory]"` /
`".[re]"` for the heavier optional dependencies (Volatility3, angr/unicorn). See
`src/corescope/` for the implementation — keep this skill's references in sync with
what the CLI actually does; don't document behavior the code doesn't have yet.

## Working directory hygiene

- Never write a real sample, memory dump, or case data into this repository. Use
  `$CORESCOPE_WORKDIR` (default `./cases/`, gitignored) or a directory outside the repo.
- Hash (`sha256sum`) any acquired sample/dump immediately, before any analysis, for chain
  of custody.

---

## Attribution

Methodology (source precedence, `references/` per domain, pitfalls file with validation
badges, `.skill` packaging) adapted from
[`fs25-claude-skill`](https://github.com/TheCodingDad-TisonK/fs25-claude-skill), generalized
from a single-target game-modding skill to the memory forensics / binary analysis / reverse
engineering domain, which has no single fixed corpus to index — every case is a new sample.
