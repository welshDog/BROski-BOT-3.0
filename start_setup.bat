@echo off
echo Starting BROski Bot 3.0 Easy Setup...

:: Check for Python installation
python --version > nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Python is not installed or not in PATH.
    echo Please install Python 3.8 or higher from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

:: Run the setup script
python easy_setup.py

:: Check if script succeeded
if %ERRORLEVEL% neq 0 (
    echo Setup encountered some issues. Please check the messages above.
) else (
    echo Setup completed successfully!
)

pause
