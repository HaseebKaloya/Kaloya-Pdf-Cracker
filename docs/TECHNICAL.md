# Technical Reference — Kaloya PDF Cracker

This document describes the internal architecture, threading model, and implementation decisions behind Kaloya PDF Cracker v1.0.

---

## Architecture Overview

The application is a three-layer system:

```
┌─────────────────────────────────────┐
│          main.py                    │  Entry point — bootstraps QApplication, loads stylesheet
├─────────────────────────────────────┤
│  gui/main_window.py (HackerMainWindow) │  All UI widgets, layout, page navigation, signals
│  gui/worker.py     (CrackerWorker)     │  QThread — runs cracker engine in background
├─────────────────────────────────────┤
│          cracker.py                 │  Core engine: hash extraction, JtR invocation, pot reading
│          john/run/                  │  John the Ripper binaries + configs + .chr files
└─────────────────────────────────────┘
```

---

## PDF Hash Extraction

Hash extraction uses the `pyhanko` library's `PdfFileReader`. It reads the PDF's `/Encrypt` dictionary and reconstructs a `$pdf$` hash string in the exact format John the Ripper expects.

Key fields extracted:

| Field | Description |
|---|---|
| `/V` | Algorithm version (1=RC4-40, 2/3=RC4-128, 4=AES-128, 5/6=AES-256) |
| `/R` | Revision — determines key derivation method |
| `/Length` | Key length in bits |
| `/P` | Permission flags |
| `udata`, `odata`, `oeseed`, `ueseed` | User/owner password hash data |
| `document_id[0]` | File identifier used in key derivation |

The resulting format:

```
$pdf$<V>*<R>*<Length>*<P>*<encrypt_metadata>*<id_len>*<id_hex>*<key_data...>
```

This hash is written to a temporary `hash.txt` file and passed to JtR.

---

## John the Ripper Integration

### Binary Selection

`find_john()` iterates a priority list of JtR executables:

```
john-avx2.exe  →  john-avx.exe  →  john-sse41.exe  →  john-sse2.exe  →  john.exe
```

The first file found on disk is selected. This ensures the fastest available instruction set is always used without requiring user configuration.

### Subprocess Execution

JtR runs as a subprocess via `subprocess.Popen` with `stdout=PIPE` and `cwd=JOHN_DIR`. The working directory is set to `john/run/` so JtR can find its `.conf`, `.chr`, and `.pot` files using relative paths.

```python
proc = subprocess.Popen(
    [john_exe, '--format=pdf', hash_file, '--wordlist=...'],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True, encoding='utf-8', errors='ignore',
    bufsize=1, cwd=JOHN_DIR
)
```

### Result Reading

Results are always read from `john.pot` via the `--show` flag rather than parsing live stdout. This is more reliable because JtR's live output format varies between runs and instruction set builds.

```python
subprocess.run([john_exe, '--show', '--format=pdf', hash_file], cwd=JOHN_DIR)
```

The output is parsed with a regex to handle both `filename:password:...` and `password (filename)` output formats.

### Cache Clearing

JtR caches cracked hashes in `john.pot`. If the same PDF is cracked twice without clearing the pot, JtR exits immediately with "No password hashes left to crack". `clear_john_pot()` strips any matching entry before each run.

---

## Threading Model

PyQt5 freezes if long-running operations block the main event loop. The application uses a `QThread` subclass (`CrackerWorker`) to isolate all JtR activity.

### Signal Map

| Signal | Type | Trigger |
|---|---|---|
| `output_signal` | `str` | Any text output from the backend |
| `finished_signal` | `(str, float)` | Password found: emits the password and elapsed time |
| `failed_signal` | `float` | Attack exhausted without result: emits elapsed time |
| `error_signal` | `str` | Fatal error or user abort |

All signal connections happen in `HackerMainWindow.start_or_abort_attack()` before the thread starts. The GUI updates in response to signals via normal Qt slot invocations — safe, because signals cross the thread boundary automatically.

### stdout Redirection

`CrackerWorker` temporarily replaces `sys.stdout` with a `StreamRedirector` instance. This intercepts `print()` calls inside `cracker.py` and re-routes them through `output_signal`, which streams them to the GUI terminal. The original stdout is restored in the `finally` block.

**Important:** Only one worker should run at a time. The current implementation enforces this — the "INITIATE CRACK" button becomes "ABORT ATTACK" while a worker is active, preventing a second worker from being created.

---

## Windows API Integration

On Windows, the standard PyQt5 title bar is light-coloured and cannot be styled via QSS. The application uses:

```python
ctypes.windll.dwmapi.DwmSetWindowAttribute(
    hwnd,
    DWMWA_USE_IMMERSIVE_DARK_MODE,  # attribute 20
    byref(ctypes.c_int(2)),
    sizeof(ctypes.c_int)
)
```

This forces the OS into dark mode for this window's title bar. A second call to `DwmSetWindowAttribute` with `DWMWA_TEXT_COLOR` (attribute 35) sets the title text color to neon green (`0x0041FF00` in COLORREF BBGGRR format). The call is wrapped in a try-except to fail silently on older Windows versions.

---

## CLI Usage

`cracker.py` is also a standalone CLI tool:

```powershell
# Wordlist attack
python cracker.py target.pdf --wordlist rockyou.txt

# Digit brute-force (4 through 6 digits)
python cracker.py target.pdf --digits 4-6

# Save result to custom file
python cracker.py target.pdf --wordlist rockyou.txt --output found.txt
```

The CLI exit code is `0` on success and `1` on failure or error.

---

## Build System

### PyInstaller

`build.spec` compiles the application in **one-folder mode** (not one-file). One-file mode is explicitly avoided because `cracker.py` resolves `john/run/` relative to `SCRIPT_DIR` at runtime. In one-file mode, the extracted temp directory path changes on each launch, breaking the relative path resolution.

The `john/run/` directory is bundled as a data tree using the `datas` list in the spec rather than `binaries`, because JtR uses companion files (`.conf`, `.chr`, `.pot`) alongside its executables.

UPX compression is enabled for the Python internals but explicitly excluded for Cygwin DLLs (`cygwin1.dll`, etc.), which break under UPX.

### Inno Setup

`installer/setup.iss` compiles the `dist/KaloyaPDFCracker/` folder into a single setup wizard. Key choices:

- **LZMA2 ultra64 compression** — maximum size reduction on the folder payload
- **Upgrade detection** — the Pascal `[Code]` section silently uninstalls any previous version before installing the new one
- **`DisableProgramGroupPage = yes`** — the default Start Menu group name is used without asking the user
- **`PrivilegesRequired = admin`** — required to write to `%ProgramFiles%`
