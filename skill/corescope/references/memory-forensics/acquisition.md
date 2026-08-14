# Memory acquisition

Only relevant when the user is capturing a live system (their own lab/authorized IR
engagement) rather than analyzing an already-acquired dump.

## Tools by target

| Target | Tool | Notes |
|---|---|---|
| Linux (live) | [LiME](https://github.com/504ensicsLabs/LiME) | Loadable kernel module; must be built against the *exact* running kernel version |
| Windows (live) | WinPmem, Magnet RAM Capture | Kernel-mode driver; run elevated |
| VMware VM | `.vmem` (+ `.vmsn`/`.vmss` snapshot metadata) | Snapshot or suspend the VM; `.vmem` alone is the raw RAM image |
| VirtualBox VM | `VBoxManage debugvm <vm> dumpguestcore --filename dump.elf` | Produces an ELF core dump Volatility3 can read directly |
| Cloud instance | Provider-specific snapshot, or agent-based (e.g. via a memory acquisition agent) | Live acquisition of a cloud VM's RAM is rarely straightforward; check provider docs first |

## Chain of custody (do this before any analysis)

```bash
sha256sum dump.raw > dump.raw.sha256
```

1. Hash the dump **immediately** after acquisition, before touching it further.
2. Work on a copy; keep the original + its hash untouched.
3. Never write the dump (or any derived artifact containing case data) into this git
   repository — see `SECURITY.md` and the root `.gitignore` (`cases/`, `*.dmp`, `*.vmem`,
   `*.raw`, `*.mem`).

## Format notes

- Raw/flat dumps (`.raw`, `.dd`, `.mem`, `.lime`) — what most acquisition tools produce.
- `.vmem` (VMware) and VirtualBox `.elf` core dumps are natively supported by Volatility3
  without conversion.
- Windows hibernation files (`hiberfil.sys`) and crash dumps (`.dmp`) are also supported,
  but are compressed/partial snapshots, not full live RAM — expect gaps.
