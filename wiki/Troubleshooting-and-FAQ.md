# Troubleshooting and Technical FAQ

This document addresses diagnostic scenarios, antivirus heuristic alerts, performance optimization, and architectural questions regarding **Kaloya PDF Cracker**.

---

## Diagnostics and Solutions

### 1. "PDF NOT ENCRYPTED" Notification

- **Root Cause**: The selected PDF does not contain an active `/Encrypt` object in its document catalog or cross-reference trailer.
- **Resolution**: The document is unlocked and requires no cryptographic processing. It can be opened directly with standard PDF readers (Adobe Acrobat, Mozilla Firefox, Google Chrome, Evince).

### 2. Antivirus or Windows Defender Heuristic Alerts (False Positive)

- **Root Cause**: Standalone distributions bundle native binaries of **John the Ripper** (`john-avx2.exe`, `john.exe`). Generic heuristic analysis engines may flag these utilities with categories such as `HackTool:Win32/PasswordStealer` or `Not-a-virus:RiskTool`.
- **Technical Context**: John the Ripper is an open-source security assessment engine standard in cybersecurity research. Kaloya PDF Cracker contains **zero telemetry, zero outbound networking code, and zero spyware**.
- **Resolution**: Add the installation directory (`%LocalAppData%\Programs\Kaloya PDF Cracker`) or application directory to your security suite's exclusion list.

### 3. Exhausted Attacks ("Password Not Found")

- **In Dynamic Digits Mode**: The password exceeds the configured digit span, or incorporates alphanumeric characters or special symbols (e.g., `Pass123`). Expand the evaluated range (e.g., `4-8`) or transition to a Dictionary Attack.
- **In Dictionary Mode**: The wordlist did not contain the exact target passphrase. Utilize an expanded wordlist (such as `rockyou.txt`) or generate a targeted dictionary reflecting known credential patterns.

### 4. Terminal State Stalled at "Waiting for target..."

- Ensure that a valid `.pdf` document was selected via the **Browse** dialog prior to initiating execution.

---

## Frequently Asked Questions

### Is Kaloya PDF Cracker completely offline?

**Yes.** The codebase contains no network sockets, remote API callers, analytics tracking, or cloud dependencies. The software can be executed on fully air-gapped systems with network interfaces disabled.

### What factors dictate candidate evaluation speed?

Throughput is primarily determined by two variables:

1. **Host CPU Microarchitecture**: Modern processors supporting AVX2 and AVX vector instructions evaluate between **50,000 and 500,000+ hashes per second**, depending on algorithm complexity.
2. **PDF Security Revision**: Earlier RC4-40 and RC4-128 algorithms compute significantly faster than modern AES-256 (Revision 5 and Revision 6) standards due to computationally intensive key derivation functions (PBKDF2 / SHA-256 / SHA-384).

### Where are recovered passwords stored?

When a password is recovered, the engine records the hash and plaintext string into the local potfile:

- Windows: `{app}\john\run\john.pot`
- Linux: `~/.john/john.pot`

Subsequent runs against an identical document check this registry first, returning the cached result immediately without re-executing attacks.

### Why are Administrator privileges not required?

The application adheres to the principle of least privilege (`asInvoker`). Installing into the user-level directory (`%LocalAppData%\Programs\`) avoids continuous UAC prompts and maintains standard desktop shortcut iconography without administrative badge overlays.

---

## Support and Bug Reports

To report issues or request enhancements:

- **Issue Tracker**: [github.com/HaseebKaloya/Kaloya-Pdf-Cracker/issues](https://github.com/HaseebKaloya/Kaloya-Pdf-Cracker/issues)
- **Developer Inquiries**: `contact.haseebkaloya@gmail.com`
- **Source Repository**: [github.com/HaseebKaloya/Kaloya-Pdf-Cracker](https://github.com/HaseebKaloya/Kaloya-Pdf-Cracker)
