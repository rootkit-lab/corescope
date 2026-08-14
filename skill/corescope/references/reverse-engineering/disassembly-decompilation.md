# Disassembly and decompilation

## Choosing a tool

| Need | Tool |
|---|---|
| Scriptable disassembly inside Python | `capstone` |
| Quick CLI look without opening a GUI | `objdump -d`, `r2 -A file` |
| Full interactive RE, free, has a decompiler | Ghidra (also scriptable headless — see below) |
| Full interactive RE, best-in-class UX, no free decompiler | IDA Free (x86/x64 only) |
| Full interactive RE, strong scripting API | Binary Ninja |
| CFG recovery / symbolic execution programmatically | `angr` |

## capstone (library, quick disassembly)

```python
from capstone import Cs, CS_ARCH_X86, CS_MODE_64

md = Cs(CS_ARCH_X86, CS_MODE_64)
for insn in md.disasm(code_bytes, base_address):
    print(f"0x{insn.address:x}:\t{insn.mnemonic}\t{insn.op_str}")
```

`code_bytes` has to be the actual code bytes already extracted (e.g. via `pyelftools`/
`pefile`/`LIEF` reading the relevant section) — capstone only disassembles, it does not
parse container formats.

## radare2 / r2pipe (CLI-first, scriptable)

```bash
r2 -A sample          # -A: run full auto-analysis on load
afl                   # list functions found
pdf @ sym.main        # disassemble (print disassembly function) at symbol/address
axt @ 0x401000        # find cross-references TO this address
```

```python
import r2pipe

r2 = r2pipe.open("sample", flags=["-2"])  # -2: suppress stderr noise
r2.cmd("aaa")  # analyze all
functions = r2.cmdj("aflj")  # JSON list of functions
```

## Ghidra headless (free, has a decompiler)

```bash
analyzeHeadless /path/to/project ProjectName -import sample.bin -postScript MyScript.py
```

Useful when you need Ghidra's decompiler output in an automated/batch pipeline rather than
interactively. Scripts run in Jython by default; use Ghidrathon for real CPython + your
normal Python environment/packages.

## Decompiler output is not ground truth

Any decompiler (Ghidra, IDA, Binary Ninja, angr's `decompiler`) **infers** variable names,
some type information, and control-flow shape (loops reconstructed from jumps). This
inference is frequently wrong in ways that look plausible:

- Renamed/generic variable names (`uVar1`, `local_28`) carry no real semantic meaning —
  do not treat a decompiler's guessed name as a fact about the program.
- Inlined or optimized functions can appear merged or missing entirely — don't conclude "no
  such check exists" from decompiled output alone; check the disassembly too.
- Reconstructed `goto`/label control flow sometimes indicates a decompiler struggling with
  a switch/jump-table, not that the original source used `goto`.

Treat the decompiler as a strong hint, verify anything load-bearing to your conclusion
against the actual disassembly.

## See also

- `references/reverse-engineering/emulation-and-symbolic-execution.md`
- `references/pitfalls/what-doesnt-work.md`
