---
title: 'Wrapping John the Ripper in a PyQt5 GUI on Windows: Architecture and Hard-Won Lessons'
published: true
description: 'A technical deep-dive into how Kaloya PDF Cracker uses QThread for non-blocking UI, UAC manifests for auto-elevation, and Inno Setup 6 for professional Windows packaging.'
tags: 'python, tutorial, security, pyqt5'
cover_image: 'https://raw.githubusercontent.com/HaseebKaloya/Kaloya-Pdf-Cracker/main/docs/images/hero_banner.png'
series: Kaloya PDF Cracker
id: 3448770
date: '2026-04-03T08:21:45Z'
---

# Wrapping John the Ripper in a PyQt5 GUI on Windows

In the [first article of this series](#), I introduced Kaloya PDF Cracker and explained the problem it solves. In this post, I want to go deeper into the technical decisions and the specific challenges I ran into while building it.

This is a walkthrough of three problems that took real effort to solve correctly:

1. Keeping the GUI responsive while the cracking engine runs
2. Getting automatic Administrator elevation without any user configuration
3. Packaging everything into a single professional Windows installer

---

## The Application Architecture

The codebase is split into three clean, independent layers. This separation is not just organisational — it is what allows the application to be extended, tested, and maintained without one layer breaking another.

```
+-----------------------------------------------+
|              PyQt5 Presentation Layer         |
|   main_window.py  +  gui/styles.qss           |
+-----------------------------------------------+
                        |
                  signals & slots
                        |
+-----------------------------------------------+
|              Worker / Logic Layer             |
|   worker.py  (runs inside QThread)            |
+-----------------------------------------------+
                        |
                  subprocess calls
                        |
+-----------------------------------------------+
|            John the Ripper Engine             |
|   john.exe  +  pdf2john.py  (bundled)         |
+-----------------------------------------------+
```

The GUI layer never calls John the Ripper directly. It communicates only with the Worker through PyQt5 signals and slots. This is the architectural decision that everything else builds on.

---

## Problem 1 — Keeping the GUI Responsive

This is the most common mistake developers make when first integrating a subprocess into a Python GUI application.

If you call `subprocess.run()` directly inside a button click handler, the entire Qt event loop blocks. The window freezes. The progress bar does not move. The Cancel button stops working. The user sees a white rectangle and assumes the application crashed.

The correct solution is `QThread`.

```python
# gui/worker.py

from PyQt5.QtCore import QThread, pyqtSignal
import subprocess
import os

class CrackingWorker(QThread):

    # Signals communicate results back to the main thread safely
    log_message = pyqtSignal(str)
    finished    = pyqtSignal(str)
    error       = pyqtSignal(str)

    def __init__(self, pdf_path, wordlist_path, john_dir):
        super().__init__()
        self.pdf_path     = pdf_path
        self.wordlist_path = wordlist_path
        self.john_dir     = john_dir
        self._stopped     = False

    def stop(self):
        self._stopped = True

    def run(self):
        # Step 1 — Extract the encrypted hash from the PDF
        self.log_message.emit("Extracting hash from PDF...")

        pdf2john = os.path.join(self.john_dir, "pdf2john.py")
        hash_file = os.path.join(self.john_dir, "hash.txt")

        result = subprocess.run(
            ["python", pdf2john, self.pdf_path],
            capture_output=True, text=True
        )

        if result.returncode != 0:
            self.error.emit("Failed to extract hash from PDF.")
            return

        with open(hash_file, "w") as f:
            f.write(result.stdout.strip())

        # Step 2 — Feed the hash to John the Ripper
        self.log_message.emit("Starting dictionary attack...")

        john_exe = os.path.join(self.john_dir, "john.exe")
        proc = subprocess.Popen(
            [john_exe, f"--wordlist={self.wordlist_path}", hash_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            cwd=self.john_dir
        )

        for line in proc.stdout:
            if self._stopped:
                proc.terminate()
                self.finished.emit("Cancelled.")
                return
            self.log_message.emit(line.strip())

        proc.wait()

        # Step 3 — Read the result from john.pot
        pot_file = os.path.join(self.john_dir, "john.pot")
        if os.path.exists(pot_file):
            with open(pot_file, "r") as f:
                content = f.read().strip()
            if content:
                password = content.split(":")[-1]
                self.finished.emit(password)
            else:
                self.finished.emit("Password not found in wordlist.")
        else:
            self.finished.emit("Attack complete. Check logs.")
```

In the main window, connecting to these signals is straightforward:

```python
# gui/main_window.py (excerpt)

self.worker = CrackingWorker(pdf_path, wordlist_path, john_dir)
self.worker.log_message.connect(self.log_area.append)
self.worker.finished.connect(self.on_finished)
self.worker.error.connect(self.on_error)
self.worker.start()
```

Because `QThread` runs on a separate OS thread, the Qt event loop continues processing on the main thread. The progress bar animates. The Cancel button works. The log area updates in real time.

---

## Problem 2 — Automatic Administrator Elevation

John the Ripper needs to write files — the `.pot` file that stores recovered passwords, and the `.log` and `.rec` files it uses for session management. On Windows 10 and 11, writing to `C:\Program Files\` requires Administrator-level access.

Without elevation, John the Ripper fails silently. The GUI shows no error, the process exits cleanly, but no password is ever recovered.

There are two common approaches to handle this. The wrong way is calling `ShellExecuteEx` with `runas` at runtime from Python — this forces elevation on every subprocess launch and creates a visible UAC prompt mid-session which confuses users.

The correct way is embedding a UAC Application Manifest directly into the compiled executable.

**`uac_manifest.xml`**

```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly
  xmlns="urn:schemas-microsoft-com:asm.v1"
  manifestVersion="1.0">

  <trustInfo xmlns="urn:schemas-microsoft-com:asm.v3">
    <security>
      <requestedPrivileges>
        <requestedExecutionLevel
          level="requireAdministrator"
          uiAccess="false"/>
      </requestedPrivileges>
    </security>
  </trustInfo>

</assembly>
```

This manifest tells Windows that the application must always run as Administrator. The UAC prompt appears exactly once — when the user double-clicks the application shortcut. After that, all subprocesses it spawns inherit the same elevated context automatically.

In the PyInstaller spec file, two settings activate this:

```python
# build.spec (excerpt)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='KaloyaPDFCracker',
    uac_admin=True,              # tells PyInstaller to set the elevation flag
    manifest='uac_manifest.xml', # embeds the XML into the EXE resources
    ...
)
```

---

## Problem 3 — A Professional Windows Installer

PyInstaller produces a folder of files and a single `.exe` entry point. Distributing a folder to non-technical users who expect a standard Windows installer is a poor experience.

Inno Setup 6 solves this. It compresses the entire application directory and produces a single self-extracting installer executable that handles installation, shortcut creation, and uninstallation automatically.

The most important lesson from building the installer was about a single flag.

**The bug:** After installation, if the user ticked "Launch Kaloya PDF Cracker" on the final page, the application launched without Administrator elevation and crashed immediately.

**The cause:** The `[Run]` section had the `runasoriginaluser` flag set. This flag explicitly tells Inno Setup to drop the elevated context it holds during installation and launch the application as the original non-admin user. That directly contradicts the `requireAdministrator` manifest in the EXE.

**The fix:** Remove `runasoriginaluser` and add `shellexec` instead.

```ini
; WRONG — drops elevation, causes crash on first launch
[Run]
Filename: "{app}\KaloyaPDFCracker.exe"; \
  Flags: nowait postinstall skipifsilent runasoriginaluser

; CORRECT — shellexec triggers a fresh UAC prompt, elevation is preserved
[Run]
Filename: "{app}\KaloyaPDFCracker.exe"; \
  Flags: shellexec nowait postinstall skipifsilent
```

This single change fixed the post-installation launch error entirely.

---

## The Lesson About Taskbar Pinning

One requested feature was programmatic pinning of the application shortcut to the Windows taskbar. This seemed straightforward. In practice, it is completely impossible.

Microsoft blocked all programmatic taskbar pinning in Windows 10 Build 1703 (the Creators Update, released April 2017). Any code, script, or installer that claims to do this is either detecting a specific older Windows version or simply does nothing silently on modern systems.

The correct solution is to tell the user to do it themselves. The installer finish page now contains a single clear line of instruction. This is not a limitation — it is the only honest approach available.

---

## Source Code and Download

**GitHub Repository:** [https://github.com/HaseebKaloya/Kaloya-Pdf-Cracker](https://github.com/HaseebKaloya/Kaloya-Pdf-Cracker)

**Download the Installer:** [https://github.com/HaseebKaloya/Kaloya-Pdf-Cracker/releases](https://github.com/HaseebKaloya/Kaloya-Pdf-Cracker/releases)

If you have questions about the QThread implementation, the UAC manifest embedding, or the Inno Setup configuration, ask in the comments and I will answer in detail.
 
  
