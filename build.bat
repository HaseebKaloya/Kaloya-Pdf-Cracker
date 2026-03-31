@echo off
:: ─────────────────────────────────────────────────────────────────────────────
:: KALOYA PDF CRACKER — One-Click Build Script
:: ─────────────────────────────────────────────────────────────────────────────

title Kaloya PDF Cracker Build
color 0A

echo.
echo  ██╗  ██╗ █████╗ ██╗      ██████╗ ██╗   ██╗ █████╗ 
echo  ██║ ██╔╝██╔══██╗██║     ██╔═══██╗╚██╗ ██╔╝██╔══██╗
echo  █████╔╝ ███████║██║     ██║   ██║ ╚████╔╝ ███████║
echo  ██╔═██╗ ██╔══██║██║     ██║   ██║  ╚██╔╝  ██╔══██║
echo  ██║  ██╗██║  ██║███████╗╚██████╔╝   ██║   ██║  ██║
echo  ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝ ╚═════╝   ╚═╝   ╚═╝  ╚═╝
echo.
echo  PDF PASSWORD CRACKER v1.0 -- BUILD SYSTEM
echo  ════════════════════════════════════════════
echo.

:: --- Check PyInstaller ---
python -m PyInstaller --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  [ERROR] PyInstaller is not installed.
    echo          Run: pip install pyinstaller
    echo.
    pause
    exit /b 1
)

echo  [1/3] Cleaning previous build artifacts...
if exist build rmdir /s /q build
if exist dist  rmdir /s /q dist
echo         Done.
echo.

echo  [2/3] Compiling with PyInstaller...
echo.
python -m PyInstaller build.spec --clean
echo.

if %errorlevel% neq 0 (
    echo  [ERROR] Build FAILED. Check the output above for errors.
    echo.
    pause
    exit /b 1
)

echo  [3/3] Build complete!
echo.
echo  ════════════════════════════════════════════
echo  OUTPUT:  dist\KaloyaPDFCracker\KaloyaPDFCracker.exe
echo  ════════════════════════════════════════════
echo.
echo  Run the EXE above to verify before building the installer.
echo.
pause
