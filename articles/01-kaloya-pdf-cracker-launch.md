---
title: 'I Built a Free, Offline PDF Password Cracker for Windows — Here is Why'
published: true
description: 'Kaloya PDF Cracker is a professional, open-source Windows desktop application for recovering forgotten PDF passwords. It runs 100% offline using the John the Ripper engine wrapped in a sleek PyQt5 GUI.'
tags: 'python, security, opensource, windows'
cover_image: 'https://raw.githubusercontent.com/HaseebKaloya/Kaloya-Pdf-Cracker/main/docs/images/hero_banner.png'
series: Kaloya PDF Cracker
id: 3448771
date: '2026-04-03T08:21:46Z'
---

# I Built a Free, Offline PDF Password Cracker for Windows

Most PDF password recovery tools on the internet share one of three problems.

They charge a monthly subscription. They require you to upload your sensitive document to a cloud server you know nothing about. Or they are powerful command-line tools with no graphical interface, making them completely inaccessible to most people.

**Kaloya PDF Cracker** is my answer to all three problems — a fully offline, completely free, open-source Windows desktop application that puts the legendary John the Ripper engine behind a clean, modern GUI.

---

## The Problem in Plain Terms

Imagine you find a password-protected PDF — a tax return from three years ago, a scanned bank statement, an old work contract. You have no memory of the password.

You search Google. Every top result is one of the following:

- A website with a giant upload button asking you to send your private financial document to "their secure server"
- A commercial tool priced at $49.99 for a single use
- A command-line utility with a 40-page manual

None of these are acceptable for a non-technical person who simply wants their own document back. That is the exact gap I wanted to fill.

---

## What is Kaloya PDF Cracker?

Kaloya PDF Cracker is a desktop application for Windows 10 and Windows 11. It accepts a locked PDF file, extracts its encrypted hash, and systematically attempts to recover the original password using dictionary attacks or brute-force combinations — all entirely on your local machine.

> **Your files never leave your computer. No internet connection is required at any point in the process.**

| Capability | Detail |
|----|-----|
| Dictionary Attack | Import any wordlist — RockYou, custom regional lists, anything |
| Brute-Force Mode | Iterates every possible character combination automatically |
| Processing | 100% local — CPU and GPU hardware only |
| Target Platform | Windows 10 and Windows 11 (64-bit) |
| License | Free and Open Source |
| Installation | Professional one-click installer — no dependencies needed |

---

## The Technology Stack

The application is built on top of three well-established technologies.

**GUI Layer — PyQt5**

The interface is built with PyQt5 using a completely custom dark stylesheet written in Qt Style Sheets (QSS). The design prioritises clarity — a single window, an obvious file picker, a visible progress area, and a clear result display.

**Cracking Core — John the Ripper (Jumbo Edition)**

John the Ripper is the industry-standard open-source password auditing engine. It has been in active development since 1997 and is used by penetration testers and security researchers worldwide. Kaloya PDF Cracker bundles the Windows Jumbo build of John the Ripper directly inside the installer so users never need to configure anything manually.

**Packaging — PyInstaller and Inno Setup 6**

PyInstaller compiles the Python application into a standalone `.exe`. Inno Setup 6 then wraps that executable and all its dependencies — including the entire John the Ripper binary directory — into a single professional Windows installer with a licence agreement, desktop shortcut, and an optional Windows startup entry.

---

## How It Works Step by Step

```
User selects a locked PDF
         |
         v
pdf2john.py extracts the encrypted hash from the PDF
         |
         v
hash is written to a temporary file
         |
         v
john.exe receives the hash + wordlist/attack mode
         |
         v
john.exe tests password candidates at hardware speed
         |
         v
recovered password is displayed in the GUI
```

The GUI remains fully responsive throughout this entire process because the John the Ripper subprocess runs inside a dedicated `QThread`, completely separate from the main application thread.

---

## The Installation Experience

One of the things I cared most about was making this feel like professional software, not a hobbyist project.

The installer is built with Inno Setup 6. It includes:

- A custom dark-themed sidebar image with neon green branding
- A full end-user licence agreement
- Automatic desktop and Start Menu shortcut creation
- An optional "Launch on Windows Startup" entry
- A proper entry in Windows "Apps and Features" with version number and publisher name

The application executable has a UAC manifest embedded directly into it requiring Administrator-level elevation on every launch. Windows displays the standard User Account Control prompt automatically — the user simply clicks Yes and the application starts with the permissions John the Ripper needs to function correctly.

---

## Download and Source Code

The installer and full source code are available on GitHub.

**Repository:** [https://github.com/HaseebKaloya/Kaloya-Pdf-Cracker](https://github.com/HaseebKaloya/Kaloya-Pdf-Cracker)

**Download v1.0.0:** [https://github.com/HaseebKaloya/Kaloya-Pdf-Cracker/releases](https://github.com/HaseebKaloya/Kaloya-Pdf-Cracker/releases)

If this project is useful to you, a star on the repository goes a long way toward helping other people discover it.

---

**Legal Notice:** Kaloya PDF Cracker is intended strictly for recovering passwords from PDF documents you legally own, or for authorised security auditing in environments you control. The author accepts no liability for misuse. 


  
