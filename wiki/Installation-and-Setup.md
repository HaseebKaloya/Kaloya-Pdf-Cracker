# Installation and Setup

This document outlines the deployment methods for **Kaloya PDF Cracker**, covering both the pre-packaged Windows installer and running from source on Windows and Linux systems.

---

## Windows Standalone Distribution (Recommended)

The standalone Windows distribution packages the Python runtime, PyQt5 graphical libraries, PyHanko cryptographic dependencies, and multi-architecture John the Ripper binaries into a single setup executable.

### Download

Obtain the latest signed release package from the repository releases:

- **[KaloyaPDFCracker_Setup_v1.0.0.exe](https://github.com/HaseebKaloya/Kaloya-Pdf-Cracker/releases)**

### Architecture and Security Attributes

- **Zero External Dependencies**: Operates independently of system Python installations, compilers, or Cygwin runtimes.
- **User-Space Deployment**: Installs directly into `%LocalAppData%\Programs\Kaloya PDF Cracker` without requiring system administrator privileges.
- **Unrestricted Desktop Integration**: Configured with standard execution rights (`asInvoker`), generating standard desktop shortcuts without Windows UAC badge overlays.
- **Persistent Potfile**: Software updates preserve existing candidate caches and cracked hash registries (`john.pot`).

---

## Running from Source (Windows and Linux)

For development or direct execution from source, follow the environment configuration below.

### Prerequisites

- **Python**: Version 3.10 through 3.14 (64-bit architecture)
- **Git**: For version control management

### Installation Steps

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/HaseebKaloya/Kaloya-Pdf-Cracker.git
   cd Kaloya-Pdf-Cracker
   ```

2. **Initialize a Virtual Environment (Recommended)**:
   - On Windows:
     ```powershell
     python -m venv venv
     .\venv\Scripts\Activate.ps1
     ```
   - On Linux:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Install Dependencies**:
   ```bash
   pip install PyQt5 pyhanko cryptography
   ```

4. **Launch Application**:
   ```bash
   python main.py
   ```

> [!NOTE]
> On Linux distributions, if John the Ripper is not located on `$PATH`, the application initiates automated provisioning through the native package manager upon starting an attack. Refer to the [Linux Platform Guide](Linux-Guide) for further details.

---

## System Requirements

| Metric | Minimum Requirement | Recommended Specification |
|---|---|---|
| Operating System | Windows 10/11 (x64), Linux (Debian, Ubuntu, Arch, Fedora) | Windows 11 (x64) or Ubuntu 22.04 LTS+ |
| Processor (CPU) | x86_64 dual-core with SSE2 support | Modern quad-core processor with **AVX2** extensions |
| Memory (RAM) | 2 GB available RAM | 4 GB+ RAM (required for multi-gigabyte dictionaries) |
| Disk Storage | 250 MB free disk space | 2 GB+ (to accommodate extended wordlists) |
| Display | 1024 × 768 display resolution | 1920 × 1080 (Full HD) |

---

## Compiling the Executable and Installer

To build the standalone binary and setup installer manually:

1. Install build tooling:
   ```bash
   pip install pyinstaller
   ```

2. Execute the PyInstaller specification:
   ```bash
   python -m PyInstaller build.spec -y --clean
   ```

3. Compile the Inno Setup distribution script:
   ```powershell
   & "C:\Program Files\Inno Setup 6\ISCC.exe" installer\setup.iss
   ```

The compiled setup installer will be output to `installer\Output\`.
