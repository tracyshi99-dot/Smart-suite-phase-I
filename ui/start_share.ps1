# SmartSuite Streamlit - 内网共享启动脚本
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "  SmartSuite Streamlit 内网共享模式" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# 获取内网 IP (优先 10.x 网段)
$ip = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -like "10.*" } | Select-Object -First 1).IPAddress
if (-not $ip) {
    $ip = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -notlike "127.*" } | Select-Object -First 1).IPAddress
}

Write-Host "同事访问地址: " -NoNewline
Write-Host "http://${ip}:8501" -ForegroundColor Green
Write-Host ""
Write-Host "把上面的链接发给同事即可。Ctrl+C 停止服务。" -ForegroundColor Yellow
Write-Host "--------------------------------------"
Write-Host ""

# 启动 Streamlit
& "$PSScriptRoot\.venv\Scripts\streamlit.exe" run "$PSScriptRoot\app.py" --server.address 0.0.0.0 --server.port 8501
