$dns = Get-DnsClientServerAddress -AddressFamily IPv4 | Where-Object { $_.ServerAddresses.Count -gt 0 }
foreach ($d in $dns) {
    Write-Host "$($d.InterfaceAlias): $($d.ServerAddresses -join ', ')"
}
