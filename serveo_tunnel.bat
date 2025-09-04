@echo off
echo ============================================
echo Serveo SSH Tunnel - Alternative to ngrok
echo ============================================
echo.
echo This will create a public tunnel to your Flask app
echo Your app must be running on port 5000
echo.
echo Press Ctrl+C to stop the tunnel
echo.
echo Starting tunnel...
echo.

ssh -R 80:localhost:5000 serveo.net

echo.
echo Tunnel stopped.
pause
