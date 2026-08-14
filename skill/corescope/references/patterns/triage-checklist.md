# Triage checklists

Copy the relevant checklist and track progress through it. Stop and report if a step
reveals something that changes the plan (e.g. sample is clearly a known benign tool) —
don't mechanically finish every step regardless of findings.

## New binary sample

```
- [ ] file <sample>                                — confirm format (ELF/PE/other) before anything else
- [ ] sha256sum <sample>                            — record hash before any modification
- [ ] strings -a -n 8 <sample> ; strings -a -e l -n 8 <sample>   — both encodings, see strings-iocs-yara.md
- [ ] entropy check per-section                     — packer-detection.md
- [ ] imports/exports (pefile/pyelftools/LIEF)       — elf-pe-basics.md, capability triage from API names
- [ ] YARA against any relevant local rule sets      — strings-iocs-yara.md
- [ ] if packed: attempt known unpacker (e.g. upx -d) — packer-detection.md
- [ ] static disassembly of the entry point / suspicious imports' call sites — disassembly-decompilation.md
- [ ] only if dynamic analysis is needed: run inside Dockerfile sandbox, --network=none
- [ ] write up findings WITH the evidence (command + output) for each claim
```

## New memory dump

```
- [ ] sha256sum <dump>                               — chain of custody, before anything else
- [ ] vol -f <dump> windows.info (or linux.info)     — confirm it parses
- [ ] windows.pslist AND windows.psscan              — diff the PID sets, see volatility3-workflow.md
- [ ] windows.pstree                                 — parent/child anomalies
- [ ] windows.cmdline                                — obfuscated/encoded command lines
- [ ] windows.netscan                                — connections tied to suspicious PIDs
- [ ] windows.malfind                                — injected code regions
- [ ] dump any suspicious process/region for static analysis — feed into the binary checklist above
- [ ] write up findings WITH the evidence (plugin + relevant output row) for each claim
```

## Deciding whether a finding is worth escalating

A finding is "worth escalating" (report as likely malicious/actionable) when **at least
two independent signals agree** — e.g. high entropy *and* tiny import table *and* dropped
into a suspicious PID's memory region — not on a single heuristic alone. Say explicitly
which signals you have and which you don't, rather than rounding up to a confident verdict
from partial evidence.
