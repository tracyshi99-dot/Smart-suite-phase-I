# Setup Windows Task Scheduler for Smart Suite Automation
# Run this script as Administrator to create the scheduled task.
#
# Options:
#   - Every hour: Checks rules hourly (recommended)
#   - Loop mode: Run continuously with 5-min interval

$ProjectPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$PythonExe = "python"
$ScriptPath = Join-Path $ProjectPath "automation_cron.py"

Write-Host "=== Smart Suite Automation Task Setup ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Project: $ProjectPath"
Write-Host "Script:  $ScriptPath"
Write-Host ""

# Option 1: Hourly task
$TaskName = "SmartSuite_Automation_Hourly"
$Action = New-ScheduledTaskAction -Execute $PythonExe -Argument "`"$ScriptPath`"" -WorkingDirectory $ProjectPath
$Trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 1) -RepetitionDuration (New-TimeSpan -Days 365)
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

try {
    Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Description "Smart Suite automation rule check (hourly)" -Force
    Write-Host "✅ Task '$TaskName' created successfully!" -ForegroundColor Green
    Write-Host "   Runs every 1 hour, checks all users' automation rules." -ForegroundColor Gray
} catch {
    Write-Host "❌ Failed to create task. Try running as Administrator." -ForegroundColor Red
    Write-Host "   Error: $_" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "--- Alternative: Run in loop mode (no Task Scheduler needed) ---" -ForegroundColor Yellow
Write-Host "  python automation_cron.py --loop 300" -ForegroundColor White
Write-Host "  (Checks every 5 minutes, runs until you stop it)" -ForegroundColor Gray
Write-Host ""
Write-Host "--- To remove the scheduled task ---" -ForegroundColor Yellow
Write-Host "  Unregister-ScheduledTask -TaskName '$TaskName' -Confirm:`$false" -ForegroundColor White
