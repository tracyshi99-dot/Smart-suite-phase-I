# Quick Lambda deploy - no pip needed (uses layers)
$ErrorActionPreference = "SilentlyContinue"
Set-Location "C:\Users\yujiashi\Desktop\SmartSuite_Phase1"

# Refresh creds
ada credentials update --account 830279064391 --provider conduit --role IibsAdminAccess-DO-NOT-DELETE --once --profile default 2>$null

# Package code only (deps are in Lambda layers)
$pkg = "$env:TEMP\ss_lambda_code"
if (Test-Path $pkg) { Remove-Item -Recurse -Force $pkg }
New-Item -ItemType Directory -Path $pkg -Force | Out-Null
Copy-Item "api\main.py" "$pkg\main.py"
Copy-Item "api\s3_storage.py" "$pkg\s3_storage.py" -ErrorAction SilentlyContinue
Copy-Item "api\__init__.py" "$pkg\__init__.py" -ErrorAction SilentlyContinue
Copy-Item "ui\engine.py" "$pkg\engine.py"
New-Item -ItemType Directory "$pkg\output" -Force | Out-Null
Copy-Item "output\users.json" "$pkg\output\users.json" -ErrorAction SilentlyContinue

# Zip and upload
$zip = "$env:TEMP\ss_lambda.zip"
if (Test-Path $zip) { Remove-Item $zip }
tar -acf $zip -C $pkg .
aws s3 cp $zip "s3://smartsuite-sync-data/lambda/smartsuite_api.zip" --profile default 2>$null
aws lambda update-function-code --function-name smartsuite-api --s3-bucket smartsuite-sync-data --s3-key "lambda/smartsuite_api.zip" --profile default 2>$null | Out-Null

Write-Host "Lambda deployed OK" -ForegroundColor Green
