# -*- mode: python ; coding: utf-8 -*-
# ─────────────────────────────────────────────────────────────────────────────
# KALOYA PDF CRACKER — PyInstaller Build Spec
# Run: pyinstaller build.spec --clean
# ─────────────────────────────────────────────────────────────────────────────

import os

block_cipher = None

# Collect all data files that must travel with the binary
added_files = [
    # GUI assets
    ('gui/logo.ico',   'gui'),
    ('gui/logo.png',   'gui'),
    ('gui/styles.qss', 'gui'),

    # John the Ripper — entire run directory (binaries + configs + .chr files)
    ('john/run/*',     'john/run'),
]

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=added_files,
    hiddenimports=[
        # PyQt5 internals that PyInstaller sometimes misses
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
        'PyQt5.sip',
        # pyhanko and its deep dependency tree
        'pyhanko',
        'pyhanko.pdf_utils',
        'pyhanko.pdf_utils.reader',
        'pyhanko.pdf_utils.generic',
        'pyhanko.pdf_utils.crypt',
        'pyhanko.pdf_utils.crypt.permissions',
        'pyhanko.pdf_utils.crypt.api',
        'pyhanko.pdf_utils.crypt.rc4',
        'pyhanko.pdf_utils.crypt.standard',
        'oscrypto',
        'certvalidator',
        'asn1crypto',
        'cryptography',
        'cryptography.hazmat',
        'cryptography.hazmat.primitives',
        'cryptography.hazmat.backends',
        # Application modules
        'cracker',
        'gui.main_window',
        'gui.worker',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Strip test / notebook bloat from the bundle
        'matplotlib',
        'numpy',
        'pandas',
        'PIL',
        'IPython',
        'jupyter',
        'tkinter',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,          # One-folder mode (not onefile) for
                                    # correct relative path resolution for john/
    name='KaloyaPDFCracker',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,                       # Compress binaries with UPX if available
    upx_exclude=[
        # Do not compress John's Cygwin DLLs — UPX breaks them
        'cygwin1.dll',
        'cygcrypto-1.1.dll',
        'cygssl-1.1.dll',
        'cygcrypto-1.0.0.dll',
        'cygssl-1.0.0.dll',
    ],
    console=False,                  # GUI app — no console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='gui/logo.ico',            # Application icon
    version='version_info.txt',     # Embed Metadata (Copyright, Name, Version)
    contents_directory='.',         # Output dependencies to Root Folder
    # ── UAC: request admin elevation on double-click ──────────────────────
    uac_admin=True,                 # Embeds requireAdministrator in the manifest
    manifest='uac_manifest.xml',    # Full manifest with UAC + DPI awareness
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[
        'cygwin1.dll',
        'cygcrypto-1.1.dll',
        'cygssl-1.1.dll',
        'cygcrypto-1.0.0.dll',
        'cygssl-1.0.0.dll',
    ],
    name='KaloyaPDFCracker',        # Output folder: dist/KaloyaPDFCracker/
)
