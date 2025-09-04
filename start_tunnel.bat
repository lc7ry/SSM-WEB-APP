@echo off
echo 🚗 Car Meet App - Starting Tunnel
echo ==================================
echo.
echo This will set up ngrok tunnel for your Flask app
echo Make sure your Flask app is running on port 5000
echo.
echo 🔍 First, let's test if your Flask app is running...
echo.
python test_flask_app.py
echo.
echo If the test above shows your Flask app is working, press any key to continue...
pause >nul
echo.
echo 🚀 Setting up tunnel...
echo.
python setup_tunnel.py
pause
