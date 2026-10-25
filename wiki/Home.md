# Kaloya PDF Cracker Documentation

Welcome to the technical documentation and reference manual for **Kaloya PDF Cracker**, a high-performance desktop application for recovering credentials and testing encryption resilience on PDF documents.

Powered by an integrated **John the Ripper (JtR)** core and **PyHanko** cryptographic parsers, Kaloya PDF Cracker combines native binary performance with a structured, thread-safe desktop interface.

---

## Architectural Principles

- **Local Execution and Data Privacy**: Operates fully offline. No external network requests, analytics libraries, or telemetry collection. Document streams and hashes remain strictly on the host system.
- **Hardware-Optimized Instruction Sets**: The engine detects CPU vector capabilities (AVX2, AVX, SSE4.1, SSE2) at runtime to maximize candidate evaluation throughput per core.
- **Cross-Platform Compatibility**: A single cross-platform code base providing an Inno Setup installer on Windows and automated package resolution on Linux.
- **Pre-Execution Cryptographic Inspection**: Rapidly validates the `/Encrypt` dictionary before allocating compute resources, preventing invalid attempts on unencrypted files.
- **Standard User Privilege Compliance**: Runs under standard user rights (`asInvoker`), avoiding mandatory UAC elevation prompts and operating within user space directories.

---

## Quick Start

1. **Load Target**: Select **Browse** in the Target Selection panel and specify the encrypted `.pdf` file. The engine validates the encryption revision instantly.
2. **Select Vector**:
   - **Dynamic Digits**: Specify a fixed length or length range (e.g., `4`, `6`, or `4-6` for PIN recovery).
   - **Dictionary**: Provide a plaintext wordlist file formatted with one candidate per line (e.g., `rockyou.txt`).
3. **Execute Attack**: Click **Initiate Crack**. Real-time candidate evaluation rates and engine logs are displayed in the embedded terminal. Upon recovery, the plaintext password is presented with single-click clipboard copying.

---

## Documentation Index

| Topic | Coverage |
|---|---|
| **[Installation and Setup](Installation-and-Setup)** | Standalone Windows distribution, environment prerequisites, source build instructions. |
| **[Usage and Attack Vectors](Usage-and-Attack-Vectors)** | Target selection, Dynamic Digits configuration, Dictionary modes, and terminal monitoring. |
| **[Linux Platform Guide](Linux-Guide)** | Architecture, dependency discovery order, and package manager integration. |
| **[Troubleshooting and FAQ](Troubleshooting-and-FAQ)** | Common runtime warnings, false positive guidance, and technical specifications. |

---

## Legal and Authorized Use Notice

> [!IMPORTANT]
> **Authorized Security Auditing Only**: Kaloya PDF Cracker is provided strictly for lawful password recovery, authorized penetration testing, forensic investigations, and cryptographic academic research.
>
> Users are strictly required to verify authorization before evaluating documents. The author (**Haseeb Kaloya**) disclaims all responsibility for unauthorized usage, non-compliance with applicable laws, or data security breaches resulting from the operation of this utility.
