# Smart Suite - Full EC2 Deployment Script
# This script: creates EC2 → uploads code → installs deps → starts Streamlit
# Usage: .\deploy_full.ps1

$ErrorActionPreference = "Continue"
$region = "us-east-1"

# --- Step 1: Check if we already have a running instance ---
Write-Host "=== Smart Suite EC2 Deployment ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "[1/6] Checking for existing SmartSuite instance..." -ForegroundColor Yellow

$existingInstances = aws ec2 describe-instances `
    --filters "Name=tag:Name,Values=SmartSuite" "Name=instance-state-name,Values=running" `
    --query "Reservations[].Instances[].InstanceId" `
    --output text --region $region 2>&1

if ($existingInstances -and $existingInstances -notmatch "error" -and $existingInstances.Trim() -ne "") {
    Write-Host "  Found existing instance: $existingInstances" -ForegroundColor Green
    $instanceId = $existingInstances.Trim()
    $ip = aws ec2 describe-instances --instance-ids $instanceId `
        --query "Reservations[0].Instances[0].PublicIpAddress" --output text --region $region
    if ($ip -and $ip -ne "None") {
        Write-Host "  Public IP: $ip" -ForegroundColor Green
        Write-Host "  URL: http://${ip}:8501" -ForegroundColor Green
        Write-Host ""
        $choice = Read-Host "Instance exists. [R]edeploy code / [N]ew instance / [Q]uit? (R/N/Q)"
        if ($choice -eq "Q") { exit }
        if ($choice -eq "R") {
            Write-Host "  Redeploying code to existing instance..." -ForegroundColor Yellow
            goto upload
        }
    }
}

# --- Step 2: Create Security Group ---
Write-Host "[2/6] Creating security group..." -ForegroundColor Yellow

$sgExists = aws ec2 describe-security-groups `
    --filters "Name=group-name,Values=smartsuite-web" `
    --query "SecurityGroups[0].GroupId" --output text --region $region 2>&1

if ($sgExists -and $sgExists -ne "None" -and $sgExists -notmatch "error") {
    $sg = $sgExists.Trim()
    Write-Host "  Using existing SG: $sg" -ForegroundColor Green
} else {
    # Get default VPC
    $vpc = aws ec2 describe-vpcs --filters "Name=isDefault,Values=true" `
        --query "Vpcs[0].VpcId" --output text --region $region
    
    $sg = aws ec2 create-security-group `
        --group-name smartsuite-web `
        --description "SmartSuite Streamlit Web Access" `
        --vpc-id $vpc --region $region `
        --query GroupId --output text 2>&1
    
    # Open ports
    aws ec2 authorize-security-group-ingress --group-id $sg --protocol tcp --port 8501 --cidr 10.0.0.0/8 --region $region 2>&1 | Out-Null
    aws ec2 authorize-security-group-ingress --group-id $sg --protocol tcp --port 22 --cidr 10.0.0.0/8 --region $region 2>&1 | Out-Null
    Write-Host "  Created SG: $sg (ports 22, 8501 open to internal)" -ForegroundColor Green
}

# --- Step 3: Create Key Pair ---
Write-Host "[3/6] Setting up key pair..." -ForegroundColor Yellow

$keyName = "smartsuite-key"
$keyFile = "$env:USERPROFILE\.ssh\smartsuite-key.pem"

$keyExists = aws ec2 describe-key-pairs --key-names $keyName --region $region 2>&1
if ($keyExists -match "error" -or $keyExists -match "InvalidKeyPair") {
    aws ec2 create-key-pair --key-name $keyName --query KeyMaterial --output text --region $region | Out-File -Encoding ascii $keyFile
    Write-Host "  Created key pair: $keyFile" -ForegroundColor Green
} else {
    Write-Host "  Key pair exists: $keyName" -ForegroundColor Green
}

# --- Step 4: Launch EC2 Instance ---
Write-Host "[4/6] Launching EC2 instance (Amazon Linux 2023, t3.small)..." -ForegroundColor Yellow

# User data script to install dependencies on boot
$userData = @"
#!/bin/bash
yum update -y
yum install -y python3.11 python3.11-pip git
pip3.11 install streamlit pandas plotly openpyxl boto3 fastapi uvicorn openai
mkdir -p /opt/smartsuite
chown ec2-user:ec2-user /opt/smartsuite
"@

$userDataB64 = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($userData))

# Get latest Amazon Linux 2023 AMI
$ami = aws ec2 describe-images `
    --owners amazon `
    --filters "Name=name,Values=al2023-ami-2023*-x86_64" "Name=state,Values=available" `
    --query "sort_by(Images, &CreationDate)[-1].ImageId" `
    --output text --region $region

Write-Host "  AMI: $ami"

$instanceId = aws ec2 run-instances `
    --image-id $ami `
    --instance-type t3.small `
    --key-name $keyName `
    --security-group-ids $sg `
    --user-data $userDataB64 `
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=SmartSuite}]" `
    --region $region `
    --query "Instances[0].InstanceId" --output text

Write-Host "  Instance ID: $instanceId" -ForegroundColor Green
Write-Host "  Waiting for instance to start..."

aws ec2 wait instance-running --instance-ids $instanceId --region $region

# Get public IP
$ip = aws ec2 describe-instances --instance-ids $instanceId `
    --query "Reservations[0].Instances[0].PublicIpAddress" --output text --region $region

if (-not $ip -or $ip -eq "None") {
    # No public IP, try private
    $ip = aws ec2 describe-instances --instance-ids $instanceId `
        --query "Reservations[0].Instances[0].PrivateIpAddress" --output text --region $region
    Write-Host "  Private IP: $ip (no public IP assigned)" -ForegroundColor Yellow
} else {
    Write-Host "  Public IP: $ip" -ForegroundColor Green
}

# Wait for SSH to be ready
Write-Host "  Waiting 60s for instance initialization..." -ForegroundColor Yellow
Start-Sleep -Seconds 60

# --- Step 5: Upload code ---
Write-Host "[5/6] Uploading Smart Suite code..." -ForegroundColor Yellow
:upload

$srcPath = Split-Path -Parent $PSScriptRoot
if (-not $srcPath) { $srcPath = $PSScriptRoot }
if (-not $srcPath) { $srcPath = "C:\Users\yujiashi\Desktop\SmartSuite_Phase1" }

# Create a zip of the necessary files
$zipPath = "$env:TEMP\smartsuite_deploy.zip"
if (Test-Path $zipPath) { Remove-Item $zipPath }

# Use tar to create archive (available on Windows 10+)
$filesToDeploy = @(
    "ui\app.py", "ui\engine.py", "ui\requirements.txt",
    "ui\smart-suite-wiki-zh.html", "ui\smart-suite-wiki.html",
    "ui\smart-suite-showcase.html", "ui\index.html",
    "ui\logo_transparent.png", "ui\logo.png",
    "ui\simulate_tab.py", "ui\zhice_engine.py",
    "ui\demo_data.py", "ui\app_zhice.py",
    "ui\.streamlit",
    "api\main.py", "api\requirements.txt", "api\__init__.py",
    "input\seo_sem_keywords.csv",
    ".env"
)

Write-Host "  Packaging files..."
$deployDir = "$env:TEMP\smartsuite_pkg"
if (Test-Path $deployDir) { Remove-Item -Recurse -Force $deployDir }
New-Item -ItemType Directory -Path $deployDir -Force | Out-Null

foreach ($f in $filesToDeploy) {
    $src = Join-Path $srcPath $f
    $dst = Join-Path $deployDir $f
    if (Test-Path $src) {
        $dstDir = Split-Path $dst -Parent
        if (-not (Test-Path $dstDir)) { New-Item -ItemType Directory -Path $dstDir -Force | Out-Null }
        Copy-Item $src $dst -Force
    }
}

# SCP upload
Write-Host "  Uploading to EC2 via SCP..."
scp -o StrictHostKeyChecking=no -i $keyFile -r "$deployDir\*" "ec2-user@${ip}:/opt/smartsuite/"

# --- Step 6: Start Streamlit ---
Write-Host "[6/6] Starting Streamlit on EC2..." -ForegroundColor Yellow

$startCmd = @"
cd /opt/smartsuite/ui && nohup python3.11 -m streamlit run app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true > /tmp/streamlit.log 2>&1 &
"@

ssh -o StrictHostKeyChecking=no -i $keyFile "ec2-user@$ip" $startCmd

Write-Host ""
Write-Host "=== DEPLOYMENT COMPLETE ===" -ForegroundColor Green
Write-Host "Instance ID: $instanceId" -ForegroundColor Cyan
Write-Host "IP Address:  $ip" -ForegroundColor Cyan
Write-Host "Smart Suite: http://${ip}:8501" -ForegroundColor Green
Write-Host ""
Write-Host "SSH Access:  ssh -i $keyFile ec2-user@$ip" -ForegroundColor Gray
Write-Host "Stop:        aws ec2 stop-instances --instance-ids $instanceId --region $region" -ForegroundColor Gray
Write-Host "Terminate:   aws ec2 terminate-instances --instance-ids $instanceId --region $region" -ForegroundColor Gray
