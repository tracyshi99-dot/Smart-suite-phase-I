# Fix WSL2 DNS when connected to Cisco AnyConnect VPN
# Run this in PowerShell as Administrator

Write-Host "=== Fixing WSL2 VPN DNS ===" -ForegroundColor Green

# Step 1: Get Cisco AnyConnect DNS servers
$vpnAdapter = Get-NetAdapter | Where-Object { $_.InterfaceDescription -Match "Cisco AnyConnect" }
if (-not $vpnAdapter) {
    Write-Host "ERROR: Cisco AnyConnect adapter not found. Are you connected to VPN?" -ForegroundColor Red
    exit 1
}
Write-Host "Found VPN adapter: $($vpnAdapter.Name)" -ForegroundColor Cyan

$vpnDns = Get-DnsClientServerAddress -InterfaceIndex $vpnAdapter.ifIndex -AddressFamily IPv4 | Select-Object -ExpandProperty ServerAddresses
Write-Host "VPN DNS servers: $($vpnDns -join ', ')" -ForegroundColor Cyan

# Step 2: Set WSL interface metric higher priority
$wslAdapter = Get-NetAdapter | Where-Object { $_.Name -Match "WSL" }
if ($wslAdapter) {
    Write-Host "Setting WSL adapter metric to 1..." -ForegroundColor Yellow
    Set-NetIPInterface -InterfaceIndex $wslAdapter.ifIndex -InterfaceMetric 1
}

# Step 3: Set Cisco AnyConnect metric to 6000 (lower priority for WSL routing)
Write-Host "Setting Cisco AnyConnect metric to 6000..." -ForegroundColor Yellow
Set-NetIPInterface -InterfaceIndex $vpnAdapter.ifIndex -InterfaceMetric 6000

# Step 4: Write DNS to WSL resolv.conf
$dnsEntries = ($vpnDns | ForEach-Object { "nameserver $_" }) -join "`n"
$wslConf = "[network]`ngenerateResolvConf = false"

Write-Host "Writing DNS config to WSL..." -ForegroundColor Yellow
wsl -d Ubuntu -u root -- bash -c "echo '$wslConf' > /etc/wsl.conf"
wsl -d Ubuntu -u root -- bash -c "echo '$dnsEntries' > /etc/resolv.conf"

# Step 5: Test
Write-Host "`n=== Testing DNS resolution ===" -ForegroundColor Green
$testResult = wsl -d Ubuntu -- bash -c "curl -s --connect-timeout 5 https://brazil-build-tools.amazon.com/toolbox/install 2>&1 | head -3"
if ($testResult) {
    Write-Host "SUCCESS! DNS is working." -ForegroundColor Green
    Write-Host $testResult
} else {
    Write-Host "Still not working. Trying alternate fix..." -ForegroundColor Yellow
    
    # Alternate: add route for VPN DNS through Windows host
    $wslGateway = wsl -d Ubuntu -- bash -c "ip route show default | awk '{print `$3}'"
    Write-Host "WSL Gateway: $wslGateway"
    
    # Try with Windows host IP as DNS (Windows will proxy)
    $windowsIp = wsl -d Ubuntu -- bash -c "ip route show default | awk '{print `$3}'"
    wsl -d Ubuntu -u root -- bash -c "echo 'nameserver $windowsIp' > /etc/resolv.conf; for dns in $($vpnDns -join ' '); do echo nameserver `$dns >> /etc/resolv.conf; done"
    
    $testResult2 = wsl -d Ubuntu -- bash -c "curl -s --connect-timeout 5 https://brazil-build-tools.amazon.com 2>&1 | head -3"
    if ($testResult2) {
        Write-Host "SUCCESS with alternate fix!" -ForegroundColor Green
    } else {
        Write-Host "DNS still not resolving. You may need to restart WSL: wsl --shutdown" -ForegroundColor Red
    }
}

Write-Host "`nDone. If it worked, run in WSL:" -ForegroundColor Cyan
Write-Host "  curl -s https://brazil-build-tools.amazon.com/toolbox/install | bash" -ForegroundColor White
