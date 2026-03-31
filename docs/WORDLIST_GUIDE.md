# Wordlist Guide — Kaloya PDF Cracker

This guide explains how dictionary attack mode works, where to find reliable wordlists, and how to prepare custom lists for targeted recovery.

---

## How Dictionary Attack Works

When you select Dictionary Attack mode and browse to a `.txt` file, Kaloya PDF Cracker passes that file directly to John the Ripper via the `--wordlist` flag. John reads each line as a candidate password and tests it against the PDF hash. The process runs at the native speed of the JtR binary for the host CPU.

No preprocessing is performed by the application. The wordlist is passed as-is. Each line in the file is treated as one password candidate.

---

## Wordlist Format

- Plain text, one password per line
- No headers or metadata
- UTF-8 encoding is preferred; ASCII also works
- No line length limit applies, but most PDF passwords are under 32 characters

---

## Recommended Public Wordlists

### General Purpose

| Wordlist | Size | Description |
|---|---|---|
| `rockyou.txt` | ~134 MB, 14.3M entries | Leaked credential database from the 2009 RockYou breach. The most widely used starting point. |
| `SecLists` (danielmiessler) | Multiple files | A curated collection maintained on GitHub: [github.com/danielmiessler/SecLists](https://github.com/danielmiessler/SecLists) |
| `CrackStation` (human-only) | ~684 MB | [crackstation.net/crackstation-wordlist-password-cracking-dictionary.htm](https://crackstation.net/crackstation-wordlist-password-cracking-dictionary.htm) |

### Targeted Lists

| Scenario | Approach |
|---|---|
| Password is a PIN | Use Digit Attack mode instead of a wordlist |
| Password is a date | Small custom list; formats like `ddmmyyyy`, `dd/mm/yyyy` |
| Password is a name + number | Custom list generated with a tool like Crunch or CUPP |
| Corporate document | Try company name, project names, and common patterns |

---

## Using the Digit Attack Instead

For numeric-only passwords, Digit Attack mode is faster and more systematic than a wordlist because it generates all combinations directly via JtR's mask engine without reading from disk.

```
4-digit PINs :   4      (tests 0000 - 9999)
6-digit PINs :   6      (tests 000000 - 999999)
4 to 6 digits:   4-6    (tests 4-digit, then 5-digit, then 6-digit in sequence)
```

---

## Creating a Custom Wordlist

If you have specific knowledge about what the password might be — a name, a birth year, a pet's name — a small focused list can succeed far faster than a large generic one.

**Simple approach (PowerShell):**

```powershell
# Create a list of variations on a base word
$base = "kaloya"
$out = "custom.txt"

$variations = @(
    $base, ($base + "123"), ($base + "2026"), ($base + "2025"),
    ($base.ToUpper()), ($base + "!"), "K@l0y@", ($base + "1234")
)
$variations | Out-File -FilePath $out -Encoding utf8
```

Then select this file as the wordlist in the Dictionary Attack panel.

---

## Performance Notes

- Wordlist size directly affects attack duration. A 134 MB list takes longer than a 1 MB list.
- Disk read speed matters for very large wordlists. An SSD will complete the read significantly faster than an HDD.
- If a wordlist attack fails, consider: (a) a different wordlist, (b) Digit Attack if the password may be numeric, or (c) a rule-based attack via the JtR CLI (`--rules`).

---

## Legal Note

Only use wordlists on PDF files you own or have explicit written authorization to test. See [DISCLAIMER.txt](../DISCLAIMER.txt) for the full terms.
