# SmartSuite Streamlit - 一键安装并启动
# 同事首次使用运行此脚本即可
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  SmartSuite Console - 首次安装启动" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

$uiDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $uiDir

# 1. 检查/创建 venv
if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "[1/3] 创建 Python 虚拟环境..." -ForegroundColor Yellow
    python -m venv .venv
} else {
    Write-Host "[1/3] 虚拟环境已存在 ✓" -ForegroundColor Green
}

# 2. 安装依赖
Write-Host "[2/3] 安装依赖..." -ForegroundColor Yellow
& ".venv\Scripts\pip3.exe" install -r requirements.txt -q

# 3. 启动
Write-Host "[3/3] 启动 SmartSuite Console..." -ForegroundColor Yellow
Write-Host ""
Write-Host "浏览器会自动打开 http://localhost:8501" -ForegroundColor Green
Write-Host "按 Ctrl+C 停止" -ForegroundColor Yellow
Write-Host "-------------------------------------"
Write-Host ""

& ".venv\Scripts\streamlit.exe" run app.py
