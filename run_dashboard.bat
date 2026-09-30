@echo off
echo Starting HMM Trading Dashboard on port 8502...
echo.

REM Check if virtual environment exists
if not exist .venv (
    echo ERROR: Virtual environment not found!
    echo Please run setup_with_uv.bat first
    pause
    exit /b 1
)

REM Activate environment
call .venv\Scripts\activate.bat

REM Run Streamlit on port 8502
streamlit run app.py --server.port 8502

REM Keep window open if there's an error
if errorlevel 1 pause
