# Linux Cross-Platform Guide

Kaloya PDF Cracker is architected to operate across both Windows and Linux environments from a single unified codebase.

---

## Linux Architecture

On Windows environments, the application utilizes pre-compiled Cygwin binaries of John the Ripper located in `john/run/`. On Linux distributions, the application interfaces directly with the native host John the Ripper engine. This ensures optimal POSIX performance, direct kernel multithreading, and native hardware optimization.

```
┌────────────────────────────────────────┐
│      gui/main_window.py / worker.py    │
└──────────────────┬─────────────────────┘
                   │
           [ OS Detection ]
          /                \
   (Windows)              (Linux)
      │                      │
Uses bundled john/run/    Auto-probes `which john`
                          OR prompts auto-install via:
                          apt / dnf / pacman / zypper
```

---

## Automatic Engine Resolution

When an attack is initialized on a Linux system, `cracker.py` resolves the binary through the host system path in the following order:

1. `shutil.which("john")` (Active `$PATH`)
2. `/usr/bin/john`
3. `/usr/sbin/john`
4. `/usr/local/bin/john`
5. `/snap/bin/john`

If an existing binary is located, execution proceeds immediately without external dependencies.

---

## Automated Package Manager Provisioning

If John the Ripper is not present when an attack is initiated, the engine identifies the underlying distribution family and provisions the package using standard graphical privilege elevation (`pkexec`):

| Distribution Family | Detected Package Manager | Elevated Execution Command |
|---|---|---|
| Ubuntu, Debian, Kali, Linux Mint, Pop!_OS | `apt-get` | `pkexec apt-get update && pkexec apt-get install -y john` |
| Fedora, RHEL, CentOS | `dnf` | `pkexec dnf install -y john` |
| Arch Linux, Manjaro, EndeavourOS | `pacman` | `pkexec pacman -S --noconfirm john` |
| openSUSE | `zypper` | `pkexec zypper install -y john` |

Live progress is streamed directly to the embedded GUI terminal (`[SYSTEM] Installing John the Ripper engine via apt-get...`). Upon package completion, execution transitions automatically into the target attack routine.

---

## Running from Source on Linux

### 1. Repository Setup

```bash
git clone https://github.com/HaseebKaloya/Kaloya-Pdf-Cracker.git
cd Kaloya-Pdf-Cracker
pip install -r requirements.txt
```

### 2. Manual Engine Installation (Optional)

If preferred, the engine can be installed prior to running the application:

```bash
# Debian / Ubuntu / Kali
sudo apt update && sudo apt install -y john

# Arch Linux
sudo pacman -S john

# Fedora
sudo dnf install john
```

### 3. Application Launch

```bash
python3 main.py
```

---

## Desktop Environment Integration

To integrate Kaloya PDF Cracker into standard XDG desktop application menus (GNOME, KDE Plasma, XFCE):

1. Create a local desktop entry:
   ```bash
   nano ~/.local/share/applications/kaloya-pdf-cracker.desktop
   ```

2. Add the following entry specification (adjust `/path/to/` to match your local installation directory):
   ```ini
   [Desktop Entry]
   Name=Kaloya PDF Cracker
   Comment=PDF Cryptographic Security and Recovery Utility
   Exec=python3 /path/to/Kaloya-Pdf-Cracker/main.py
   Icon=/path/to/Kaloya-Pdf-Cracker/gui/logo.png
   Terminal=false
   Type=Application
   Categories=Utility;Security;
   ```

3. Save and close. The application will be immediately indexed by the desktop launcher.
