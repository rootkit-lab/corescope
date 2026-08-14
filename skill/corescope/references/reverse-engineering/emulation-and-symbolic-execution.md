# Emulation and symbolic execution

## unicorn — lightweight CPU emulation

Good for running a small, self-contained routine (a decryption/decoding loop, a hash/checksum
function, a suspected shellcode blob) without needing the whole process/OS context.

```python
from unicorn import Uc, UC_ARCH_X86, UC_MODE_64
from unicorn.x86_const import UC_X86_REG_RIP

ADDRESS = 0x1000
mu = Uc(UC_ARCH_X86, UC_MODE_64)
mu.mem_map(ADDRESS, 2 * 1024 * 1024)
mu.mem_write(ADDRESS, code_bytes)
mu.reg_write(UC_X86_REG_RIP, ADDRESS)
mu.emu_start(ADDRESS, ADDRESS + len(code_bytes))
```

You are responsible for setting up memory, registers, and stubbing any external calls the
snippet makes (`hook_add` on `UC_HOOK_INTR`/`UC_HOOK_MEM_INVALID` to catch and handle syscalls
or unmapped access instead of crashing the emulation). This is the tradeoff versus running it
for real in the sandbox: full control and safety, but you must model everything it touches.

## angr — CFG recovery and symbolic execution

```python
import angr

proj = angr.Project("sample", auto_load_libs=False)
cfg = proj.analyses.CFGFast()  # static control-flow graph
print(len(cfg.functions), "functions found")

state = proj.factory.entry_state()
simgr = proj.simulation_manager(state)
simgr.explore(find=0x401234)  # symbolically explore toward a target address
```

`auto_load_libs=False` avoids pulling in and analyzing every shared library dependency,
which is almost always what you want for a single-sample triage (much faster, avoids angr
getting lost inside libc internals).

`CFGFast` is a static heuristic recovery (fast, occasionally misses indirect
jumps/obfuscated control flow); `CFGEmulated` is slower but simulates execution to resolve
more indirect edges. Start with `CFGFast`; fall back to `CFGEmulated` if the recovered graph
looks obviously incomplete around a region you care about.

Symbolic execution scales poorly with path count (path explosion) — always bound it: a
`find=` target address, a max step count, or `avoid=` to prune known-irrelevant branches
(e.g. licensing/telemetry paths) before exploring further.

## When to use which

| Situation | Use |
|---|---|
| "What does this specific 200-byte decoder loop output for this input?" | `unicorn` |
| "What are all the functions in this binary and how do they call each other?" | `angr` `CFGFast` |
| "Is there an input that reaches this specific address/check?" | `angr` symbolic exploration |
| "I just need to read the disassembly, no execution" | `capstone` / radare2 (see `disassembly-decompilation.md`) |
