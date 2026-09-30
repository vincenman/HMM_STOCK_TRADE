@echo off
echo ========================================
echo UV Setup for HMM Trading Dashboard
echo ========================================
echo.

echo [1/5] Creating Python 3.12 virtual environment with UV...
uv venv --python 3.12

if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    echo Make sure UV is installed: https://github.com/astral-sh/uv
    pause
    exit /b 1
)

echo [OK] Virtual environment created
echo.

echo [2/5] Activating environment...
call .venv\Scripts\activate.bat

echo [OK] Environment activated
echo.

echo [3/5] Installing core packages with UV...
uv pip install streamlit plotly yfinance pandas numpy scikit-learn

echo.
echo [4/5] Installing additional packages...
uv pip install sqlalchemy bcrypt python-dotenv pytest pytest-cov colorlog python-dateutil pytz

echo.
echo [5/5] Installing hmmlearn (with Python 3.12 this should work!)...
uv pip install hmmlearn

echo.
echo ========================================
echo SETUP COMPLETE!
echo ========================================
echo.
echo To start the dashboard:
echo   1. Activate environment: .venv\Scripts\activate
echo   2. Run dashboard: streamlit run app.py
echo.
echo Or simply run: run_dashboard.bat
echo.
pause
