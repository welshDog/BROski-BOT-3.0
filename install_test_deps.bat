@echo off
echo Installing test dependencies for BROski Bot 3.0...
echo.

:: Activate virtual environment
call .venv\Scripts\activate.bat

:: Install pytest and related packages
pip install pytest pytest-xdist pytest-cov

:: Install development dependencies
pip install -r docs/dev_requirements.txt

echo.
echo Test dependencies installed successfully!
pause
