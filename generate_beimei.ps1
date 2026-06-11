# Generate beimei article
$templateDir = 'C:\Users\yujiashi\Desktop\SmartSuite_Phase1\templates\sell_design'
$outputPath = 'C:\Users\yujiashi\Desktop\SmartSuite_Phase1\output\batch_003\04_zhibu\u4e9au9a6cu900au5317u7f8eu7ad9u5b8cu5168u89e3u8bfb.json'

$outputDir = Split-Path $outputPath -Parent
if (-not (Test-Path $outputDir)) { New-Item -ItemType Directory -Path $outputDir -Force | Out-Null }

function New-Uuid { return [guid]::NewGuid().ToString() }

function Clone-Object { param($obj); return ($obj | ConvertTo-Json -Depth 50 | ConvertFrom-Json) }

function Replace-Ids {
    param($obj)
    if ($null -eq $obj) { return }
    if ($obj -is [System.Management.Automation.PSCustomObject]) {
        foreach ($prop in @($obj.PSObject.Properties)) {
            if (($prop.Name -eq 'id' -or $prop.Name -eq 'uuid') -and $prop.Value -is [string] -and $prop.Value -match '^[0-9a-f]{8}-') {
                $prop.Value = New-Uuid
            } elseif ($prop.Value -is [System.Management.Automation.PSCustomObject]) {
                Replace-Ids $prop.Value
            } elseif ($prop.Value -is [System.Collections.IEnumerable] -and $prop.Value -isnot [string]) {
                foreach ($item in $prop.Value) { Replace-Ids $item }
            }
        }
    }
}

function Set-WidgetText {
    param($widget, [string]$text, [string]$inlineStyleRangesJson = '[]', [string]$entityRangesJson = '[]', [string]$entityMapJson = '{}')
    $escapedText = $text.Replace('\', '\\').Replace('"', '\"')
    $draftJson = '{"blocks":[{"key":"1e07k","text":"' + $escapedText + '","type":"unstyled","depth":0,"inlineStyleRanges":' + $inlineStyleRangesJson + ',"entityRanges":' + $entityRangesJson + ',"data":{}}],"entityMap":' + $entityMapJson + '}'
    $draftObj = $draftJson | ConvertFrom-Json
    $widget.content = ($draftObj | ConvertTo-Json -Depth 10)
}

Write-Host 'Loading templates...'
$bodyT = Get-Content "$templateDir\body.json" -Raw | ConvertFrom-Json
$labelT = Get-Content "$templateDir\label.json" -Raw | ConvertFrom-Json
$titleT = Get-Content "$templateDir\title.json" -Raw | ConvertFrom-Json
$overviewT = Get-Content "$templateDir\overview.json" -Raw | ConvertFrom-Json
$sTitleT = Get-Content "$templateDir\s_title.json" -Raw | ConvertFrom-Json
$contentT = Get-Content "$templateDir\content.json" -Raw | ConvertFrom-Json
$table3T = Get-Content "$templateDir\table3.json" -Raw | ConvertFrom-Json
$remarkT = Get-Content "$templateDir\remark.json" -Raw | ConvertFrom-Json

Write-Host 'Templates loaded. Building...'
Write-Host 'Done setup'