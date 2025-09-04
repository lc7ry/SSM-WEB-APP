Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Serveo SSH Tunnel - Alternative to ngrok" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "This will create a public tunnel to your Flask app" -ForegroundColor Yellow
Write-Host "Your app must be running on port 5000" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C to stop the tunnel" -ForegroundColor Yellow
Write-Host ""
Write-Host "Starting tunnel..." -ForegroundColor Green
Write-Host ""

try {
    ssh -R 80:localhost:5000 serveo.net
} catch {
    Write-Host ""
    Write-Host "Tunnel stopped or error occurred." -ForegroundColor Red
}

Write-Host ""
Read-Host "Press Enter to exit"
