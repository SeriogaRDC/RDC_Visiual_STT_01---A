@echo off
REM === Portable launcher for RDC_Visual_STT_01 ===

REM 1. Set script dir as working dir
cd /d %~dp0

REM 2. Check if venv exists, if not, create it
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

REM 3. Activate venv
call venv\Scripts\activate.bat

REM 4. Upgrade pip
python -m pip install --upgrade pip

REM 5. Install requirements
if exist requirements.txt (
    echo Installing dependencies...
    pip install -r requirements.txt
) else (
    echo No requirements.txt found. Skipping pip install.
)

REM 6. Run the main program
python ollama_interface_fixed.py

REM 7. Pause so window stays open if error
pause
