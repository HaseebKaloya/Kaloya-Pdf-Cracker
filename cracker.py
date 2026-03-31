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

# John executables in priority order (fastest first)
JOHN_CANDIDATES = [
    "john-avx2.exe",
    "john-avx.exe",
    "john-sse41.exe",
    "john-sse2.exe",
    "john.exe",
]


def find_john() -> Optional[str]:
    """Find the best (fastest) available john executable."""
    for name in JOHN_CANDIDATES:
        path = os.path.join(JOHN_DIR, name)
        if os.path.isfile(path):
            return path
    return None


# PDF Hash Extraction

try:
    from pyhanko.pdf_utils.reader import PdfFileReader
    PYHANKO_OK = True
except ImportError:
    PYHANKO_OK = False


def extract_pdf_info(pdf_path: str):
    """Returns (hash_string, algo_str) or (None, None)."""
    if not PYHANKO_OK:
        return None, None
    try:
        with open(pdf_path, "rb") as f:
            reader = PdfFileReader(f, strict=False)
            enc = reader.encrypt_dict
            if not enc or enc.get("/Filter") != "/Standard":
                return None, None

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
            return hash_str, algo_map.get(algorithm, f"Algorithm-{algorithm}")

    except Exception as e:
        print(f"{RED}[ERROR]{RESET} Could not read PDF: {e}")
        return None, None


# John the Ripper Engine Integration

def clear_john_pot(john_exe: str, hash_file: str):
    """
    Remove any cached result for this hash from john.pot so John
    doesn't skip it and report 'No password hashes left to crack'.
    """
    pot_file = os.path.join(JOHN_DIR, "john.pot")
    if not os.path.isfile(pot_file):
        return
    # Read the hash we're cracking
    with open(hash_file, "r") as hf:
        our_hash = hf.read().strip()
    if not our_hash:
        return
    # Read all pot lines and remove matching ones
    with open(pot_file, "r", encoding="utf-8", errors="ignore") as pf:
        lines = pf.readlines()
    new_lines = [l for l in lines if our_hash not in l]
    if len(new_lines) != len(lines):
        with open(pot_file, "w", encoding="utf-8") as pf:
            pf.writelines(new_lines)
        print(f"  {CYAN}Cleared cached result from john.pot{RESET}")


def run_john(john_exe: str, hash_file: str, wordlist: Optional[str] = None, mask: Optional[str] = None) -> Optional[str]:
    """
    Call John the Ripper as a subprocess.
    Streams output silently and shows a clean progress spinner.
    Returns the cracked password string, or None.
    """
    cmd = [john_exe, "--format=pdf", hash_file]
    if wordlist:
        cmd.append(f"--wordlist={wordlist}")
    elif mask:
        cmd.append(f"--mask={mask}")

    found_password = None
    start_time     = time.time()

    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="ignore",
            bufsize=1,
            cwd=JOHN_DIR
        )

        spinner = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        spin_idx = 0

        for line in proc.stdout:
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
        proc.terminate()
        return None

    sys.stdout.write("\r" + " " * 50 + "\r")
    sys.stdout.flush()

    # ALWAYS read from john.pot for the result (100% reliable)
    if not found_password:
        found_password = read_from_pot(john_exe, hash_file)

    return found_password


def read_from_pot(john_exe: str, hash_file: str) -> Optional[str]:
    """Ask John to show cracked passwords via --show flag."""
    try:
        result = subprocess.run(
            [john_exe, "--show", "--format=pdf", hash_file],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
            cwd=JOHN_DIR
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
    if not john_exe:
        print(f"{RED}[ERROR]{RESET} John the Ripper not found in: {JOHN_DIR}")
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
