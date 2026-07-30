# Smart Suite - One-click Start All Services
# Double-click this file or run: .\start_all.ps1

$UI_DIR = "$PSScriptRoot\ui"
$VENV = "$UI_DIR\.venv\Scripts"

Write-Host "🚀 Starting Smart Suite services..." -ForegroundColor Cyan

# Kill any existing Streamlit processes
Get-Process -Name "streamlit" -ErrorAction SilentlyContinue | Stop-Process -Force 2>$null

# Start 8501 (Main UI)
Write-Host "  [1/2] Starting Main UI on port 8501..." -ForegroundColor Green
Start-Process -FilePath "$VENV\streamlit.exe" -ArgumentList "run", "$UI_DIR\app.py", "--server.port", "8501" -WindowStyle Minimized

# Start 8502 (POC Review UI)
Write-Host "  [2/2] Starting POC Review UI on port 8502..." -ForegroundColor Green
Start-Process -FilePath "$VENV\streamlit.exe" -ArgumentList "run", "$UI_DIR\app_review.py", "--server.port", "8502" -WindowStyle Minimized

Start-Sleep -Seconds 3
Write-Host ""
Write-Host "✅ All services started!" -ForegroundColor Green
Write-Host "   Main UI:       http://localhost:8501" -ForegroundColor White
Write-Host "   POC Review:    http://localhost:8502" -ForegroundColor White
Write-Host ""
Write-Host "Press any key to open Main UI in browser..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
Start-Process "http://localhost:8501"
