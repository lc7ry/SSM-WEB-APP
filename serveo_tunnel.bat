@echo off
echo Starting Serveo SSH tunnel for SuliStreetMeet...
echo Make sure your Flask app is running on port 5000 first!
echo.
echo If app is not running, open another command prompt and run: python app.py
echo.
echo Starting tunnel...
ssh -R 80:localhost:5000 serveo.net
pause
