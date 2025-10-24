@echo off
echo ========================================
echo SuliStreetMeet Auto Server Starter
echo ========================================
echo.

echo Starting Flask application...
start /B python app.py
timeout /t 5 /nobreak > nul

echo Checking if Flask app is running...
curl -s http://localhost:5000 > nul 2>&1
if %errorlevel% neq 0 (
    echo Flask app failed to start. Please check for errors.
    pause
    exit /b 1
)

echo Flask app is running successfully!

echo Starting tunnel...
python setup_tunnel.py 3

echo.
echo Server and tunnel should now be running.
echo Press Ctrl+C to stop everything.
pause
