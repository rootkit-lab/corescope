# Volatility3 workflow

Volatility3 (`pip install volatility3`, CLI entry point `vol`) is the rank-1 tool for
memory dump analysis. Unlike Volatility2, it auto-detects the OS/kernel from the image
itself — there is no manual `imageinfo`/profile-selection step.

```bash
vol -f dump.raw windows.info      # sanity check: can Volatility3 parse this image at all?
vol -f dump.raw <plugin> [args]
```

First run for a given kernel version may need to fetch a symbol table (ISF) from the
remote symbol server — requires network the first time; cache it locally afterwards.

## Standard triage order

1. **`windows.info`** / **`linux.info`** — confirm the image parses, get kernel version.
2. **`windows.pslist`** then **`windows.psscan`** — see "pslist vs psscan" below, always run both.
3. **`windows.pstree`** — parent/child relationships; look for anomalies (e.g. `cmd.exe`
   spawned by `wmiplayer.exe`, `powershell.exe` spawned by `winword.exe`).
4. **`windows.cmdline`** — command lines of running processes; obfuscated/base64/encoded
   PowerShell is a strong signal.
5. **`windows.netscan`** — active/listening/closed connections; look for unexpected
   external IPs tied to a suspicious PID from step 2-3.
6. **`windows.malfind`** — flags memory regions that are executable + writable and have
   no backing file on disk (classic code-injection indicator: process hollowing, reflective
   DLL injection, shellcode).
7. **`windows.dlllist`** / **`windows.handles`** — loaded modules / open handles for a
   specific suspicious PID (`--pid <n>`).

Linux equivalents: `linux.pslist`, `linux.psaux`, `linux.bash` (recovered bash history from
memory), `linux.netstat`, `linux.malfind`, `linux.lsmod` (loaded kernel modules — check for
rootkits hiding themselves from `lsmod`).

## pslist vs psscan (do not skip this)

- **`pslist`** walks the OS's normal doubly-linked list of `EPROCESS` structures. A rootkit
  using DKOM (Direct Kernel Object Manipulation) unlinks its own process from this list —
  `pslist` will not show it.
- **`psscan`** scans physical memory pages for the `EPROCESS` pool tag directly, independent
  of the linked list. It finds hidden and recently-terminated processes, at the cost of some
  false positives (stale/freed structures).
- **Always run both and diff the PID sets.** A PID in `psscan` but not in `pslist` is a
  strong hiding indicator worth investigating with `dlllist`/`malfind` on that PID.

## Extracting an artifact for further (static) analysis

```bash
vol -f dump.raw -o ./out windows.pslist --pid 1234 --dump   # dumps the process executable
vol -f dump.raw -o ./out windows.memmap --pid 1234 --dump   # dumps its full address space
vol -f dump.raw -o ./out windows.dumpfiles --pid 1234
```

Then hand the dumped artifact to `corescope bin` / `references/binary-analysis/` — memory
forensics and static binary analysis are usually the same investigation, not separate ones.

## Symbol tables (ISF) for Linux/macOS

Windows symbol tables are fetched automatically. For Linux, you generally need to build an
ISF matching the *exact* kernel banner string from the dump using `dwarf2json` against a
kernel with matching debug symbols — mismatched symbols produce silently wrong output
(fields misaligned), not an error. If output looks structurally wrong (e.g. every process
has the same absurd PID), suspect a symbol mismatch before suspecting a bug.

## See also

- `references/memory-forensics/acquisition.md` — getting a dump in the first place.
- `references/pitfalls/what-doesnt-work.md` — several Volatility-specific traps.
