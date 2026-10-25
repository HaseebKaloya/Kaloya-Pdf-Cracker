#!/usr/bin/env python3
"""
KALOYA PDF CRACKER v1.0
Professional PDF Password Recovery Tool
"""

import argparse
import os
import sys
import time
import subprocess
import re
import threading
import shutil
import platform
from typing import Optional

# ─────────────────────────────────────────────
# CONSTANTS & PATHS
# ─────────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
JOHN_DIR   = os.path.join(SCRIPT_DIR, "john", "run")

# Windows John executables in priority order (fastest first)
JOHN_CANDIDATES = [
    "john-avx2.exe",
    "john-avx.exe",
    "john-sse41.exe",
    "john-sse2.exe",
    "john.exe",
]


def find_john() -> Optional[str]:
    """Find the best available john executable (Windows or Linux)."""
    if sys.platform == "win32":
        for name in JOHN_CANDIDATES:
            path = os.path.join(JOHN_DIR, name)
            if os.path.isfile(path):
                return path
        return None
    else:
        # 1. Check system PATH (standard for Kali, Parrot, Ubuntu)
        which_john = shutil.which("john")
        if which_john:
            return which_john

        # 2. Check standard Linux install locations
        common_paths = [
            "/usr/sbin/john",
            "/usr/bin/john",
            "/usr/local/bin/john",
            "/snap/bin/john",
        ]
        for cp in common_paths:
            if os.path.isfile(cp) and os.access(cp, os.X_OK):
                return cp

        # 3. Check local bundled binary if present
        local_elf = os.path.join(JOHN_DIR, "john")
        if os.path.isfile(local_elf) and os.access(local_elf, os.X_OK):
            return local_elf

        return None


def install_linux_john(output_callback=None) -> bool:
    """
    Attempts to install John the Ripper on Linux using the system package manager.
    Uses pkexec (PolicyKit GUI auth) or sudo.
    Streams output via output_callback if provided.
    """
    if sys.platform == "win32":
        return False

    def emit(msg: str):
        if output_callback:
            output_callback(msg)
        else:
            print(msg, end="")

    # Detect package manager
    pkg_mgr = None
    install_args = []
    if shutil.which("apt-get"):
        pkg_mgr = "apt-get"
        install_args = ["install", "-y", "john"]
    elif shutil.which("dnf"):
        pkg_mgr = "dnf"
        install_args = ["install", "-y", "john"]
    elif shutil.which("pacman"):
        pkg_mgr = "pacman"
        install_args = ["-S", "--noconfirm", "john"]
    elif shutil.which("zypper"):
        pkg_mgr = "zypper"
        install_args = ["install", "-y", "john"]

    if not pkg_mgr:
        emit("[ERROR] No supported Linux package manager found (apt-get, dnf, pacman, zypper).\n")
        return False

    emit(f"[SYSTEM] Detected Linux package manager: {pkg_mgr}\n")
    emit(f"[SYSTEM] Requesting system authorization to install John the Ripper...\n")

    is_root = False
    try:
        is_root = (os.geteuid() == 0)
    except AttributeError:
        pass

    if is_root:
        cmd = [pkg_mgr] + install_args
    elif shutil.which("pkexec"):
        cmd = ["pkexec", pkg_mgr] + install_args
    elif shutil.which("sudo"):
        cmd = ["sudo", pkg_mgr] + install_args
    else:
        cmd = [pkg_mgr] + install_args

    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="ignore",
            bufsize=1
        )
        for line in proc.stdout:
            emit(f"  {line.strip()}\n")
        proc.wait()

        if proc.returncode == 0:
            emit("[SUCCESS] John the Ripper installation completed successfully!\n")
            return find_john() is not None
        else:
            emit(f"[ERROR] Installation exited with code {proc.returncode}\n")
            return False

    except Exception as e:
        emit(f"[ERROR] Could not launch installer: {e}\n")
        return False


def get_john_cwd_and_pot(john_exe: str):
    """Returns (cwd_directory, pot_file_path) appropriate for Windows or Linux."""
    if sys.platform == "win32":
        return JOHN_DIR, os.path.join(JOHN_DIR, "john.pot")

    # On Linux:
    if os.path.dirname(john_exe) == JOHN_DIR:
        return JOHN_DIR, os.path.join(JOHN_DIR, "john.pot")

    home_pot = os.path.expanduser("~/.john/john.pot")
    return SCRIPT_DIR, home_pot


# PDF Hash Extraction

try:
    from pyhanko.pdf_utils.reader import PdfFileReader
    PYHANKO_OK = True
except ImportError:
    PYHANKO_OK = False


def check_pdf_encryption(pdf_path: str):
    """
    Inspects a PDF to check its encryption status.
    Returns: (status, hash_string, algo_or_detail)
      - ("ENCRYPTED", hash_str, algo_name)
      - ("NOT_ENCRYPTED", None, "File has no password protection")
      - ("UNSUPPORTED", None, filter_name)
      - ("ERROR", None, error_message)
    """
    if not os.path.isfile(pdf_path):
        return "ERROR", None, "File does not exist"
    if not PYHANKO_OK:
        return "ERROR", None, "pyhanko library is not available"

    try:
        with open(pdf_path, "rb") as f:
            reader = PdfFileReader(f, strict=False)
            enc = reader.encrypt_dict
            if not reader.encrypted or not enc:
                return "NOT_ENCRYPTED", None, "File has no password protection"

            filt = enc.get("/Filter")
            if filt != "/Standard":
                return "UNSUPPORTED", None, f"Custom DRM / Unsupported Filter: {filt}"

            algorithm   = enc.get("/V")
            length      = enc.get("/Length", 40)
            permissions = enc["/P"]
            revision    = enc["/R"]
            enc_meta    = str(int(reader.security_handler.encrypt_metadata))
            doc_id      = reader.document_id[0]

            key_len_map = {2: 32, 3: 32, 4: 32, 5: 48, 6: 48}
            max_kl      = key_len_map.get(revision, 48)

            pwds = []
            for key in ("udata", "odata", "oeseed", "ueseed"):
                data = getattr(reader.security_handler, key, None)
                if data:
                    data = data[:max_kl]
                    pwds.extend([str(len(data)), data.hex()])

            hash_str = "*".join(map(str, [
                f"$pdf${algorithm}", revision, length, permissions,
                enc_meta, len(doc_id), doc_id.hex(), "*".join(pwds)
            ]))

            algo_map = {
                1: "RC4-40bit", 2: "RC4-128bit", 3: "RC4-128bit",
                4: "AES-128",   5: "AES-256",    6: "AES-256"
            }
            algo_name = algo_map.get(algorithm, f"Algorithm-{algorithm}")
            return "ENCRYPTED", hash_str, algo_name

    except Exception as e:
        return "ERROR", None, str(e)


def extract_pdf_info(pdf_path: str):
    """Returns (hash_string, algo_str) or (None, None). Kept for backwards compatibility."""
    status, hash_str, algo = check_pdf_encryption(pdf_path)
    if status == "ENCRYPTED":
        return hash_str, algo
    return None, None


# John the Ripper Engine Integration

def clear_john_pot(john_exe: str, hash_file: str):
    """
    Remove any cached result for this hash from john.pot so John
    doesn't skip it and report 'No password hashes left to crack'.
    """
    _, pot_file = get_john_cwd_and_pot(john_exe)
    if not os.path.isfile(pot_file):
        return
    try:
        with open(hash_file, "r") as hf:
            our_hash = hf.read().strip()
        if not our_hash:
            return
        with open(pot_file, "r", encoding="utf-8", errors="ignore") as pf:
            lines = pf.readlines()
        new_lines = [l for l in lines if our_hash not in l]
        if len(new_lines) != len(lines):
            with open(pot_file, "w", encoding="utf-8") as pf:
                pf.writelines(new_lines)
            print(f"  {CYAN}Cleared cached result from {os.path.basename(pot_file)}{RESET}")
    except Exception:
        pass


def get_windows_flags():
    """Returns (creationflags, startupinfo) to prevent console window popups on Windows."""
    flags = 0
    si = None
    if sys.platform == "win32":
        flags = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
        si = subprocess.STARTUPINFO()
        si.dwFlags |= getattr(subprocess, "STARTF_USESHOWWINDOW", 1)
        si.wShowWindow = getattr(subprocess, "SW_HIDE", 0)
    return flags, si


active_proc: Optional[subprocess.Popen] = None


def abort_current_run():
    """Immediately terminates the active John the Ripper process if running."""
    global active_proc
    if active_proc and active_proc.poll() is None:
        try:
            active_proc.terminate()
            if sys.platform == "win32":
                flags, si = get_windows_flags()
                subprocess.run(
                    ["taskkill", "/F", "/T", "/PID", str(active_proc.pid)],
                    capture_output=True,
                    creationflags=flags,
                    startupinfo=si
                )
            else:
                try:
                    active_proc.kill()
                except Exception:
                    pass
        except Exception:
            pass


def run_john(john_exe: str, hash_file: str, wordlist: Optional[str] = None, mask: Optional[str] = None, stop_check=None) -> Optional[str]:
    """
    Call John the Ripper as a subprocess.
    Streams output silently and shows a clean progress spinner.
    Returns the cracked password string, or None.
    """
    global active_proc
    cmd = [john_exe, "--format=pdf", hash_file]
    if wordlist:
        cmd.append(f"--wordlist={wordlist}")
    elif mask:
        cmd.append(f"--mask={mask}")

    found_password = None
    start_time     = time.time()
    flags, si      = get_windows_flags()
    cwd_dir, _     = get_john_cwd_and_pot(john_exe)

    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="ignore",
            bufsize=1,
            cwd=cwd_dir,
            creationflags=flags,
            startupinfo=si
        )
        active_proc = proc

        spinner = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        spin_idx = 0

        for line in proc.stdout:
            if stop_check and not stop_check():
                proc.terminate()
                try:
                    proc.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    proc.kill()
                return None

            line_s = line.strip()
            if not line_s:
                continue

            spin_idx = (spin_idx + 1) % len(spinner)
            spin_char = spinner[spin_idx]

            # Display a clean, non-garbled progress line
            elapsed = time.time() - start_time
            sys.stdout.write(f"\r  {CYAN}{spin_char} John is cracking...{RESET}  {YELLOW}Elapsed: {elapsed:.1f}s{RESET}   ")
            sys.stdout.flush()

        proc.wait()

    except FileNotFoundError:
        print(f"\n{RED}[ERROR]{RESET} John executable not found: {john_exe}")
        return None
    except KeyboardInterrupt:
        if proc:
            proc.terminate()
        return None
    finally:
        active_proc = None

    sys.stdout.write("\r" + " " * 50 + "\r")
    sys.stdout.flush()

    # ALWAYS read from john.pot for the result (100% reliable)
    if not found_password:
        found_password = read_from_pot(john_exe, hash_file)

    return found_password


def read_from_pot(john_exe: str, hash_file: str) -> Optional[str]:
    """Ask John to show cracked passwords via --show flag."""
    try:
        flags, si  = get_windows_flags()
        cwd_dir, _ = get_john_cwd_and_pot(john_exe)
        result = subprocess.run(
            [john_exe, "--show", "--format=pdf", hash_file],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
            cwd=cwd_dir,
            creationflags=flags,
            startupinfo=si
        )
        output = result.stdout.strip()
        # Output format: "pdf.pdf:462151:..."  or "462151 (pdf.pdf)"
        for line in output.splitlines():
            # "filename:password:..." format
            if ":" in line and not line.startswith("0 ") and not line.startswith("1 "):
                parts = line.split(":")
                if len(parts) >= 2:
                    pwd = parts[1].strip()
                    if pwd:
                        return pwd
            # "password (filename)" format
            m = re.match(r"^(.+?)\s+\(", line)
            if m:
                candidate = m.group(1).strip()
                if candidate and len(candidate) < 64:
                    return candidate
    except Exception:
        pass
    return None


# Main Loop

def print_banner():
    print(f"""{CYAN}{BOLD}
  ██╗  ██╗ █████╗ ██╗      ██████╗ ██╗   ██╗ █████╗
  ██║ ██╔╝██╔══██╗██║     ██╔═══██╗╚██╗ ██╔╝██╔══██╗
  █████╔╝ ███████║██║     ██║   ██║ ╚████╔╝ ███████║
  ██╔═██╗ ██╔══██║██║     ██║   ██║  ╚██╔╝  ██╔══██║
  ██║  ██╗██║  ██║███████╗╚██████╔╝   ██║   ██║  ██║
  ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝ ╚═════╝   ╚═╝   ╚═╝  ╚═╝
{RESET}{YELLOW}          PDF PASSWORD CRACKER v1.0{RESET}
{CYAN}  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}
""")


def main():
    print_banner()

    parser = argparse.ArgumentParser(
        description="Kaloya PDF Cracker v4.0 — Dynamic Digits & Wordlists",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("pdf", help="Path to the locked PDF file")
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--wordlist", help="Path to the wordlist file")
    group.add_argument("--digits", help="Digit lengths to try (e.g. '4-6' or '6')")
    
    parser.add_argument("--output", default="result.txt",
                        help="File to save the cracked password (default: result.txt)")
    args = parser.parse_args()

    # ── Validate inputs ────────────────────────────────
    if not os.path.isfile(args.pdf):
        print(f"{RED}[ERROR]{RESET} PDF not found: {args.pdf}")
        sys.exit(1)

    # ── Find John ─────────────────────────────────────
    john_exe = find_john()
    if not john_exe and sys.platform != "win32":
        print(f"\n  {YELLOW}[NOTICE]{RESET} John the Ripper not found on Linux. Installing...")
        if install_linux_john():
            john_exe = find_john()

    if not john_exe:
        if sys.platform == "win32":
            print(f"{RED}[ERROR]{RESET} John the Ripper not found in: {JOHN_DIR}")
        else:
            print(f"{RED}[ERROR]{RESET} John the Ripper not found. Please run: sudo apt install john")
        sys.exit(1)

    pdf_size_mb = os.path.getsize(args.pdf) / (1024 * 1024)
    print(f"  {BOLD}PDF File  :{RESET}  {args.pdf}  ({pdf_size_mb:.1f} MB)")

    # ── Step 1: Extract Hash ───────────────────────────
    print(f"\n  {BOLD}[Step 1]{RESET} Analyzing PDF encryption...")

    hash_str, algo = extract_pdf_info(args.pdf)
    hash_file = os.path.join(SCRIPT_DIR, "hash.txt")

    if hash_str:
        print(f"  {GREEN}✔ Encrypted!{RESET}  Algorithm: {YELLOW}{algo}{RESET}")
        with open(hash_file, "w") as hf:
            hf.write(hash_str + "\n")
        print(f"  {CYAN}Hash saved → hash.txt{RESET}")
    else:
        # Try to use existing hash.txt
        if os.path.isfile(hash_file) and os.path.getsize(hash_file) > 0:
            print(f"  {YELLOW}[WARN]{RESET} Using existing hash.txt")
        else:
            print(f"{RED}[ERROR]{RESET} Could not extract hash. Is pyhanko installed?")
            print(f"         Run: pip install pyhanko")
            sys.exit(1)

    # Clear any cached result so John doesn't skip this hash
    clear_john_pot(john_exe, hash_file)

    # ── Step 2: Crack with John ────────────────────────
    start_time     = time.time()
    found_password = None
    
    if args.wordlist:
        if not os.path.isfile(args.wordlist):
            print(f"{RED}[ERROR]{RESET} Wordlist not found: {args.wordlist}")
            sys.exit(1)
        print(f"\n  {BOLD}[Step 2]{RESET} Launching John the Ripper (Wordlist Mode)...")
        print(f"  Wordlist : {YELLOW}{os.path.basename(args.wordlist)}{RESET}")
        print(f"\n{CYAN}{'━'*54}{RESET}\n")
        
        found_password = run_john(john_exe, hash_file, wordlist=os.path.abspath(args.wordlist))
        
    elif args.digits:
        try:
            if "-" in args.digits:
                min_len, max_len = map(int, args.digits.split("-"))
            else:
                min_len = max_len = int(args.digits)
        except ValueError:
            print(f"{RED}[ERROR]{RESET} Invalid format for --digits. Use '4-6' or '6'.")
            sys.exit(1)
            
        print(f"\n  {BOLD}[Step 2]{RESET} Launching John the Ripper (Dynamic Digits: {min_len} to {max_len})...")
        print(f"\n{CYAN}{'━'*54}{RESET}\n")
        
        try:
            for length in range(min_len, max_len + 1):
                mask = "?d" * length
                sys.stdout.write(f"\r  {YELLOW}▶ Starting {length}-digit attack...{RESET}     \r")
                sys.stdout.flush()
                
                found_password = run_john(john_exe, hash_file, mask=mask)
                if found_password:
                    break
        except KeyboardInterrupt:
            print(f"\n\n  {YELLOW}[STOPPED]{RESET} Interrupted by user.")

    elapsed = time.time() - start_time

    # ── Cleanup ─────────────────────────────────────────
    if os.path.isfile(hash_file):
        try:
            os.remove(hash_file)
        except OSError:
            pass

    print(f"\n{CYAN}{'━'*54}{RESET}")

    # ── Result ─────────────────────────────────────────
    if found_password:
        print(f"\n  {GREEN}{BOLD}PASSWORD FOUND! 🎉{RESET}")
        print(f"  {'─'*50}")
        print(f"  Password  :  {GREEN}{BOLD}{found_password}{RESET}")
        print(f"  Time      :  {elapsed:.2f} seconds")
        print(f"  {'─'*50}")

        with open(args.output, "w") as f:
            f.write(f"PDF File  : {args.pdf}\n")
            f.write(f"Password  : {found_password}\n")
            f.write(f"Time      : {elapsed:.2f}s\n")
        print(f"\n  {CYAN}Result saved → {args.output}{RESET}\n")
    else:
        print(f"\n  {RED}{BOLD}PASSWORD NOT FOUND ❌{RESET}")
        print(f"  Time      :  {elapsed:.2f} seconds")
        print(f"  Hint: Try a different wordlist.\n")


if __name__ == "__main__":
    main()
