@echo off
echo ====================================
echo Ensemble Trading Dashboard Launcher
echo ====================================
echo.

REM Check if NASDAQ.csv exists
if not exist NASDAQ.csv (
    echo WARNING: NASDAQ.csv not found!
    echo.
    echo Generating sample data...
    python generate_sample_data.py
    echo.
)

echo Starting Streamlit dashboard...
echo.
echo The dashboard will open in your browser automatically.
echo Press Ctrl+C to stop the server.
echo.

streamlit run app.py

pause
