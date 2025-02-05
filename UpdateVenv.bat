@echo off
REM Check if .\venv exists
if exist ".\venv\Scripts\activate" (
    echo Virtual environment exists.
    REM Activate the virtual environment and install requirements
    call .\venv\Scripts\activate
    pip install -r requirements.txt
    echo Requirements installed successfully.
) else (
    echo Virtual environment does not exist.
    REM Create a new virtual environment
    python -m venv .\venv
    REM Activate the new virtual environment
    call .\venv\Scripts\activate
    REM Install requirements
    pip install -r requirements.txt
    echo Virtual environment created and requirements installed.
)

pause
