@echo off
setlocal

:: Set root to this batch file's directory
set "ROOT=%~dp0"
set "APPDIR=%ROOT%"

echo.
echo [🧠 GHOSTDRIVE LAUNCHER]
echo Starting GhostDrive from: %APPDIR%
echo.

:: Activate the virtual environment
call "%APPDIR%\venv\Scripts\activate.bat"

:: Launch ghostcli.py
python "%APPDIR%\ghostcli.py"

:: Error handling
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [❌] GhostDrive failed to start. Check for missing files or model path.
    pause
)

endlocal
