@echo off
echo ========================================
echo Phase 4 Setup - Paper Trading Features
echo ========================================
echo.

echo [1/4] Activating virtual environment...
call .venv\Scripts\activate.bat

echo.
echo [2/4] Checking syntax...
python test_phase4_syntax.py
if errorlevel 1 (
    echo.
    echo ERROR: Syntax errors found!
    pause
    exit /b 1
)

echo.
echo [3/4] Installing reportlab for PDF generation...
uv pip install reportlab

echo.
echo [4/4] Creating reports directory...
if not exist reports mkdir reports

echo.
echo ========================================
echo PHASE 4 SETUP COMPLETE!
echo ========================================
echo.
echo New Features Available:
echo   - Paper Trading (real-time simulation)
echo   - PDF Report Generation
echo   - Trade Notifications
echo   - Enhanced Export
echo.
echo To start:
echo   run_dashboard.bat
echo.
echo Then go to "Paper Trading" tab!
echo.
pause
