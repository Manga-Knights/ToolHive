@echo off
:: Resolve launcher.py relative to this batch file (in the same directory)
set "SCRIPT_DIR=%~dp0"
set "LAUNCHER=%SCRIPT_DIR%launcher.py"

if not exist "%LAUNCHER%" (
    echo Error: launcher.py not found at "%LAUNCHER%"
    exit /b 1
)

:: Run launcher.py in the same CMD window
python "%LAUNCHER%" %*
:: If python fails, try py
if errorlevel 1 py "%LAUNCHER%" %*
