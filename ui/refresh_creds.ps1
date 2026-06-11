# Auto-refresh AWS credentials every 45 minutes
# Run this in a separate PowerShell window: .\refresh_creds.ps1

Write-Host "Starting auto-refresh (every 45 min)..."
while ($true) {
    Write-Host "$(Get-Date -Format 'HH:mm:ss') Refreshing credentials..."
    ada credentials update --account 830279064391 --provider conduit --role IibsAdminAccess-DO-NOT-DELETE --once --profile default
    Write-Host "$(Get-Date -Format 'HH:mm:ss') Done. Next refresh in 45 min."
    Start-Sleep -Seconds 2700
}
