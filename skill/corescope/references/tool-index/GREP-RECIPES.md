# Grep / search recipes

Canned commands for quickly answering common questions. Run the real command and quote
its actual output — these are starting points, not answers to memorize.

## Identify the file

```bash
file sample                 # format, arch, stripped/not stripped, static/dynamic
sha256sum sample             # hash before doing anything else
```

## ELF

```bash
readelf -h sample            # ELF header: type, machine, entry point
readelf -d sample            # dynamic section: NEEDED libs, RPATH
readelf -S sample            # section headers + sizes (spot unusually named/sized sections)
nm -D sample                  # dynamic symbols (works even if partially stripped)
objdump -d sample | less     # full disassembly, quick look without a GUI
ldd sample                   # resolved shared library dependencies (only run on trusted-enough samples; ldd can execute the binary's dynamic loader logic — prefer readelf -d for anything untrusted)
```

## PE (via objdump/mingw tools or `pefile` in Python — see `elf-pe-basics.md`)

```bash
python3 -c "import pefile; pe = pefile.PE('sample.exe'); print(pe.dump_info())"
```

## Strings / IOC leads

```bash
strings -a -n 8 sample                       # single-byte strings
strings -a -e l -n 8 sample                  # UTF-16LE strings — check this too, always
strings -a sample | grep -Ei 'https?://|\.onion|cmd\.exe|powershell|CreateRemoteThread'
```

## radare2 quick recipes

```bash
r2 -A -q -c 'afl' sample                     # analyze + list functions, then quit
r2 -A -q -c 'iij' sample                     # imports, as JSON
r2 -A -q -c 'axt @ main' sample              # cross-references to `main`
```

## Volatility3 quick recipes

```bash
vol -f dump.raw windows.pslist | grep -i <process-name>
vol -f dump.raw windows.psscan > psscan.txt
vol -f dump.raw windows.pslist > pslist.txt
diff <(awk '{print $1}' pslist.txt) <(awk '{print $1}' psscan.txt)   # PIDs only in psscan = hiding candidates
```

## YARA

```bash
yara -r rules.yar sample_dir/                # recursive scan of a directory
```
