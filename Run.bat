@echo off
REM Check for Python installation
python --version
IF %ERRORLEVEL% NEQ 0 (
    echo Python is not installed. Please install Python first.
    pause
    exit /b 1
)

REM Upgrade pip
python -m pip install --upgrade pip

REM Install required packages
python -m pip install tk
python -m pip install ttkbootstrap

echo All packages installed successfully.
pause
