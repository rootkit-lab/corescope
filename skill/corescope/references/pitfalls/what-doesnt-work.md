# Pitfalls — what doesn't work

Known traps in this domain. Badges: ✅ VALIDATED (widely documented, mechanically verifiable
fact) · ⚠️ PARTIAL (true in the common case, has real exceptions) · 📚 REFERENCE (standard
tool/library documented behavior, included because it's easy to assume otherwise).

Check this file before finalizing any analysis conclusion.

---

### ✅ Default `strings` misses UTF-16LE text in Windows binaries

```bash
# ❌ Wrong — finds only single-byte-encoded strings
strings sample.exe

# ✅ Correct — also check UTF-16LE (wide char), very common in PE malware
strings -e l sample.exe
```
Evidence: `strings`'s default mode scans for runs of single-byte printable characters;
Win32 `wchar_t` strings are 2 bytes per character with a null byte between each ASCII byte,
which the default scan does not recognize as text at all.

---

### ✅ `pslist` alone misses hidden/unlinked processes

```
❌ Wrong:   windows.pslist only, treat the output as the complete process list
✅ Correct: run windows.pslist AND windows.psscan, diff the PID sets
```
Evidence: `pslist` walks the OS's linked list of process objects; DKOM-based hiding
techniques unlink the process from that list. `psscan` scans memory pool tags directly and
is not fooled by list unlinking. See `references/memory-forensics/volatility3-workflow.md`.

---

### ⚠️ "High entropy" and "packed" are not the same as "malicious"

```
❌ Wrong:   entropy is high in a section → label the sample malicious
✅ Correct: entropy/packing is a signal that static analysis is incomplete; verify capability separately
```
Commercial software routinely packs/obfuscates for IP protection (license enforcement,
anti-piracy). Compressed resource sections (icons, images) are also naturally
high-entropy and are not "packed code" at all — check *which* section before drawing a
conclusion.

---

### ✅ Running an unknown sample directly on the analyst's host

```
❌ Wrong:   double-click / execute the sample on your own machine "just to see what it does"
✅ Correct: always inside the Dockerfile sandbox, --network=none, disposable/revertable
```
There is no reliable way to fully contain an unknown sample's behavior by inspection alone
before running it — treat every unclassified sample as capable of persistence, credential
theft, or lateral movement until proven otherwise.

---

### ⚠️ Decompiler variable/function names are not ground truth

```
❌ Wrong:   report "the function checkLicense() does X" because the decompiler labeled it that
✅ Correct: decompilers infer names/types; verify meaning from actual logic/disassembly, not the label
```
See `references/reverse-engineering/disassembly-decompilation.md` — this applies to Ghidra,
IDA, Binary Ninja, and angr's decompiler equally.

---

### 📚 `angr` symbolic execution without bounds will not finish

```
❌ Wrong:   simgr.explore() with no find/avoid/step bound on a large binary
✅ Correct: always bound with find=, avoid=, or a step/time limit
```
Path explosion is the default failure mode of symbolic execution, not an edge case —
budget for it from the start. See
`references/reverse-engineering/emulation-and-symbolic-execution.md`.

---

### ⚠️ A stripped binary is harder, not unanalyzable

```
❌ Wrong:   "no symbols, so we can't determine anything about this function"
✅ Correct: structure (control flow, strings, imports, calling convention) still holds without symbols
```
Symbol stripping removes names, not code. Static analysis, disassembly, and even
decompilation all still work — they're just less immediately readable.

---

## Quick reference

| Trap | Correct approach | Badge |
|---|---|---|
| `strings` (default) on a PE | `strings -e l` too | ✅ |
| `pslist` only | `pslist` + `psscan`, diff | ✅ |
| High entropy = malicious | Signal only, verify capability separately | ⚠️ |
| Run unknown sample on host | Sandbox, `--network=none` | ✅ |
| Trust decompiler names | Verify against disassembly | ⚠️ |
| Unbounded symbolic execution | Bound with `find=`/`avoid=`/steps | 📚 |
| "Stripped = unanalyzable" | Structure still holds | ⚠️ |
