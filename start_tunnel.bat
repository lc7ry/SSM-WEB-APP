@echo off
echo Starting ngrok tunnel for SuliStreetMeet...
echo Make sure your Flask app is running on port 5000 first!
echo.
echo If app is not running, open another command prompt and run: python app.py
echo.
echo Starting tunnel...
ngrok http 5000
pause
