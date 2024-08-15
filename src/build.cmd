@echo off

:: Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. Please install Python 3.12 to use this script.
    goto end
)

:: Check for PyInstaller
pyinstaller --version >nul 2>&1
if %errorlevel% neq 0 (
    echo PyInstaller is not installed. Please install PyInstaller to use this script.
    goto end
)

:: If both checks pass, run PyInstaller
pyinstaller --onefile --icon "Icon1.ico" "mtf_20240521.py"

:end
pause
