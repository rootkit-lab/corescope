# Anti-debug / anti-VM / anti-analysis tricks

Assume any real-world sample may try to detect that it's being analyzed and change
behavior (or refuse to run at all). Recognize these rather than being blocked by them.

## Anti-debug (Windows)

- `IsDebuggerPresent()` / `CheckRemoteDebuggerPresent()` — direct API check.
- `PEB.BeingDebugged` flag read directly, bypassing the API (harder to hook/patch generically).
- Timing checks around a code block using `rdtsc` — an attached debugger with breakpoints
  makes execution measurably slower.
- `NtQueryInformationProcess` with `ProcessDebugPort`/`ProcessDebugFlags` — lower-level than
  `IsDebuggerPresent`, same intent.
- Exception-based tricks (e.g. deliberately triggering `INT3`/`OutputDebugString` and
  checking how it's handled) to detect a debugger intercepting exceptions.

## Anti-VM / anti-sandbox

- Registry keys / files left by common hypervisors (VMware Tools paths, VirtualBox guest
  additions).
- MAC address OUI prefixes belonging to VMware/VirtualBox/QEMU virtual NICs.
- `CPUID` hypervisor-present bit, or vendor string leaking through CPUID leaves.
- Environment fingerprints typical of automated sandboxes: single CPU core, low RAM, short
  uptime, generic/default hostname or username (`DESKTOP-XXXXX`, `user`), absence of typical
  user documents/recent files.
- Sleep/timeout evasion: sample sleeps far longer than a sandbox's analysis window, or
  checks wall-clock time deltas around a `Sleep()` call to detect time-acceleration by the
  analysis tooling.

## Practical implications for corescope workflows

- Static analysis (`references/binary-analysis/`) is unaffected by any of this — do it first.
- For dynamic analysis, run inside the `Dockerfile` sandbox but **expect it to be detected**
  as a VM/container; note that as a finding itself ("sample checks for VM artifacts before
  proceeding" is a real, reportable behavior), rather than assuming a lack of observed
  activity means the sample is benign.
- If a specific anti-debug check is blocking analysis and you need past it, patch/NOP the
  specific check (after locating it via `disassembly-decompilation.md`) rather than trying
  to make the environment indistinguishable from bare metal — that arms race is rarely worth
  it for a single-sample triage.
