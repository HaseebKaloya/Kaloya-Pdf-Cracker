# Usage and Attack Vectors

This document describes the operational workflow, attack vectors, and runtime controls available in **Kaloya PDF Cracker**.

---

## Target Selection and Cryptographic Pre-Check

### Loading a Target File

Select the **Browse** button in the **Target Selection** panel and locate the target `.pdf` document.

### Inspection Mechanism

Upon selection, the internal cryptographic parser (`pyhanko`) parses the document header, cross-reference tables, and trailer objects to analyze the `/Encrypt` dictionary:

- **Algorithm and Revision Identification**: Identifies the encryption handler and key length:
  - Standard Security Handler (Revision 2, 3, or 4: RC4-40, RC4-128, AES-128)
  - ISO 32000-2 / Extension Level 3 (Revision 5 or 6: AES-256)
- **Unencrypted File Guard**: If an unencrypted document is loaded, the application intercepts execution immediately with the following notification:
  > *"This PDF file does NOT have any password protection. It is already unlocked and can be opened directly."*
  This ensures compute resources are not allocated against unlocked documents.

---

## Dynamic Digits (Mask Attack)

Numeric PINs and passwords containing exclusively digits (`0` through `9`) are prevalent across automated exports such as utility bills, banking records, payroll summaries, and official tax statements.

### Execution Mechanism

Rather than reading millions of numeric strings from disk storage, the **Dynamic Digits** vector instructs the John the Ripper engine to generate permutations directly within processor cache memory using high-throughput mask substitution (`?d?d?d...`).

### Length Formats and Throughput

Enter the target length format in the **Length** input field:

| Input Specification | Evaluation Scope | Combinations | Approximate Execution (AVX2) |
|---|---|---|---|
| `4` | 4-digit numeric sequence (`0000` to `9999`) | 10,000 | < 0.20 seconds |
| `6` | 6-digit numeric sequence (`000000` to `999999`) | 1,000,000 | < 2.50 seconds |
| `4-6` | Sequential evaluation of 4-digit, 5-digit, and 6-digit sequences | 1,110,000 | < 3.00 seconds |
| `6-8` | Sequential evaluation of 6-digit through 8-digit sequences | 111,000,000 | 1.0 - 3.0 minutes |

> [!TIP]
> When auditing financial statements, attempt length `4` or `6` first. The majority of automated institution-generated PDFs rely on 4-digit or 6-digit strings derived from birth dates or card identification digits.

---

## Dictionary Attack

When targeting user-defined passphrases containing alphabetic words, common patterns, or alphanumeric combinations, the **Dictionary Attack** vector offers the highest probability of recovery.

### Procedure

1. Enable the **Dictionary Attack (File)** option.
2. Select the file browser to locate your target wordlist (any plain text file with a `.txt` extension).
3. Verify that the wordlist is formatted with one candidate password per line, encoded in standard UTF-8 or ASCII format.

### Reference Public Wordlists

| Wordlist | Volume | Application Scope |
|---|---|---|
| **rockyou.txt** | ~14.3 million entries (134 MB) | Standard baseline wordlist with high coverage across common user-generated passwords. |
| **SecLists** | Multi-category collections | Structured wordlists categorized by context, names, and industry patterns ([github.com/danielmiessler/SecLists](https://github.com/danielmiessler/SecLists)). |
| **Targeted Custom Lists** | Variable size | Lists generated via profiling utilities (`cupp`, `crunch`) based on known subject parameters. |

---

## Live Engine Terminal and Real-Time Controls

The **Live Hack Terminal** streams unbuffered diagnostic information from the underlying engine:

- **Candidate Processing Rate**: Displays current hash calculation speeds and completion percentages.
- **ANSI Control Sequence Sanitization**: Terminal escape codes are parsed and sanitized, rendering clean monospace status feeds in the user interface.
- **Thread-Safe Process Termination (`ABORT CRACK`)**:
  - While an attack is active, the primary execution button dynamically transforms into **Abort Crack**.
  - Selecting Abort terminates the active worker thread and sends an immediate `SIGTERM` / process kill signal to `john.exe` and background worker subprocesses, preventing orphaned instances or thread deadlocks.

---

## Password Recovery and potfile Persistence

Upon successful password recovery:

1. An audible completion indicator sounds.
2. A recovery dialogue displays:
   - Target PDF filename.
   - Total execution duration (e.g., `Time Elapsed: 1.42s`).
   - Plaintext recovered password.
   - One-click clipboard copy utility.
3. The recovered hash and plaintext password are recorded into the persistent `john.pot` database. If the same document is processed in subsequent runs, the software retrieves the cached credential instantly.
