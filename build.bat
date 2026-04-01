@echo off
:: ─────────────────────────────────────────────────────────────────────────────
:: KALOYA PDF CRACKER — Full Build Pipeline
:: Step 1: Compile EXE with PyInstaller
:: Step 2: Compile Installer with Inno Setup
:: ─────────────────────────────────────────────────────────────────────────────

title Kaloya PDF Cracker — Build Pipeline
color 0A

echo.
echo  ██╗  ██╗ █████╗ ██╗      ██████╗ ██╗   ██╗ █████╗ 
echo  ██║ ██╔╝██╔══██╗██║     ██╔═══██╗╚██╗ ██╔╝██╔══██╗
echo  █████╔╝ ███████║██║     ██║   ██║ ╚████╔╝ ███████║
echo  ██╔═██╗ ██╔══██║██║     ██║   ██║  ╚██╔╝  ██╔══██║
echo  ██║  ██╗██║  ██║███████╗╚██████╔╝   ██║   ██║  ██║
echo  ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝ ╚═════╝   ╚═╝   ╚═╝  ╚═╝
echo.
echo  PDF PASSWORD CRACKER v1.0 -- FULL BUILD PIPELINE
echo  ════════════════════════════════════════════════════
echo.

:: ─────────────────────────────────────────────────────────────────────────────
:: PRE-FLIGHT CHECKS
:: ─────────────────────────────────────────────────────────────────────────────

:: Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  [ERROR] Python is not installed or not in PATH.
    echo.
    pause
    exit /b 1
)

:: Check PyInstaller
python -m PyInstaller --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  [ERROR] PyInstaller not found. Run: pip install pyinstaller
    echo.
    pause
    exit /b 1
)

:: Check Inno Setup (common install path)
set ISCC_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe
if not exist "%ISCC_PATH%" (
    set ISCC_PATH=C:\Program Files\Inno Setup 6\ISCC.exe
)
if not exist "%ISCC_PATH%" (
    echo  [WARNING] Inno Setup 6 not found. Installer step will be skipped.
    echo            Download from: https://jrsoftware.org/isinfo.php
    set SKIP_INSTALLER=1
) else (
    set SKIP_INSTALLER=0
)

echo  [OK] Pre-flight checks passed.
echo.

:: ─────────────────────────────────────────────────────────────────────────────
:: STEP 1: CLEAN PREVIOUS BUILD
:: ─────────────────────────────────────────────────────────────────────────────
echo  [1/3] Cleaning previous build artifacts...
if exist build  rmdir /s /q build
if exist dist   rmdir /s /q dist
echo         Done.
echo.

:: ─────────────────────────────────────────────────────────────────────────────
:: STEP 2: BUILD EXE WITH PYINSTALLER
:: ─────────────────────────────────────────────────────────────────────────────
echo  [2/3] Compiling EXE with PyInstaller (UAC + Admin manifest embedded)...
echo.
python -m PyInstaller build.spec --clean
echo.

if %errorlevel% neq 0 (
    echo  [ERROR] PyInstaller build FAILED. See output above.
    echo.
    pause
    exit /b 1
)

echo  [OK] EXE compiled successfully.
echo       Output: dist\KaloyaPDFCracker\KaloyaPDFCracker.exe
echo.

:: ─────────────────────────────────────────────────────────────────────────────
:: STEP 3: BUILD INSTALLER WITH INNO SETUP
:: ─────────────────────────────────────────────────────────────────────────────
if "%SKIP_INSTALLER%"=="1" (
    echo  [SKIP] Inno Setup not found — installer step skipped.
    goto :done
)

echo  [3/3] Building installer with Inno Setup 6...
echo.
"%ISCC_PATH%" installer\setup.iss
echo.

if %errorlevel% neq 0 (
    echo  [ERROR] Inno Setup build FAILED. See output above.
    echo.
    pause
    exit /b 1
)

echo  [OK] Installer compiled successfully.
echo       Output: installer\Output\KaloyaPDFCracker_Setup_v1.0.0.exe
echo.

:done
echo.
echo  ════════════════════════════════════════════════════
echo  BUILD COMPLETE
echo  ════════════════════════════════════════════════════
echo  EXE       :  dist\KaloyaPDFCracker\KaloyaPDFCracker.exe
echo  INSTALLER :  installer\Output\KaloyaPDFCracker_Setup_v1.0.0.exe
echo.
echo  UAC Admin  : ENABLED — double-click will prompt for elevation
echo  64-bit only: ENFORCED
echo  Compression: LZMA2 Ultra64
echo  ════════════════════════════════════════════════════
echo.
pause
