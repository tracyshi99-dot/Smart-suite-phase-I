# 一键同步本地数据到 Streamlit Cloud
# 用法: .\sync_to_cloud.ps1

Write-Host "🔄 Syncing to Streamlit Cloud..." -ForegroundColor Cyan

# 1. 复制最新 metrics 数据到 demo_output
$metricsSource = "output\metrics"
$metricsDest = "ui\demo_output\metrics"
if (Test-Path $metricsSource) {
    if (-not (Test-Path $metricsDest)) { mkdir $metricsDest -Force | Out-Null }
    Copy-Item "$metricsSource\*.csv" $metricsDest -Force
    Write-Host "  ✅ Metrics data synced" -ForegroundColor Green
}

# 2. Git add, commit, push
git add ui/app.py ui/engine.py ui/demo_output/
git commit -m "Sync latest data to Cloud $(Get-Date -Format 'yyyy-MM-dd HH:mm')" 2>$null
git push origin main

Write-Host ""
Write-Host "✅ Done! Cloud will update in 1-2 minutes." -ForegroundColor Green
Write-Host "   https://smart-suite-phase-i-jzvrqtgxpmvzkssfc3bnnw.streamlit.app" -ForegroundColor Yellow
