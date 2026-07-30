# ============================================================
# Smart Suite EC2 Deployment (One-Click)
# ============================================================
# 用法: 在 PowerShell 中运行 .\deploy_smartsuite.ps1
# 前提: aws credentials 已配置 (ada credentials update)
# ============================================================

$ErrorActionPreference = "Continue"
$region = "us-east-1"
$instanceType = "t3.small"
$sgId = "sg-08ebc83436fa2d89c"  # Already created: smartsuite-web
$instanceProfileName = "SmartSuiteEC2Profile"  # Already created with Bedrock access

Write-Host "=== Smart Suite EC2 Deployment ===" -ForegroundColor Cyan
Write-Host ""

# --- Step 1: Open ports on security group (idempotent) ---
Write-Host "[1/5] Configuring security group ports..." -ForegroundColor Yellow
aws ec2 authorize-security-group-ingress --group-id $sgId --ip-permissions "IpProtocol=tcp,FromPort=8501,ToPort=8501,IpRanges=[{CidrIp=10.0.0.0/8}]" --region $region 2>&1 | Out-Null
aws ec2 authorize-security-group-ingress --group-id $sgId --ip-permissions "IpProtocol=tcp,FromPort=22,ToPort=22,IpRanges=[{CidrIp=10.0.0.0/8}]" --region $region 2>&1 | Out-Null
Write-Host "  Ports 22, 8501 configured (10.0.0.0/8)" -ForegroundColor Green

# --- Step 2: Get latest AMI ---
Write-Host "[2/5] Getting latest Amazon Linux 2023 AMI..." -ForegroundColor Yellow
$ami = aws ec2 describe-images `
    --owners amazon `
    --filters "Name=name,Values=al2023-ami-2023*-x86_64" "Name=state,Values=available" `
    --query "sort_by(Images, &CreationDate)[-1].ImageId" `
    --output text --region $region
Write-Host "  AMI: $ami" -ForegroundColor Green

# --- Step 3: Create Key Pair (if not exists) ---
Write-Host "[3/5] Setting up key pair..." -ForegroundColor Yellow
$keyName = "smartsuite-deploy-key"
$keyFile = "$env:USERPROFILE\.ssh\$keyName.pem"
$keyCheck = aws ec2 describe-key-pairs --key-names $keyName --region $region 2>&1
if ($keyCheck -match "InvalidKeyPair") {
    New-Item -ItemType Directory -Path "$env:USERPROFILE\.ssh" -Force | Out-Null
    aws ec2 create-key-pair --key-name $keyName --query KeyMaterial --output text --region $region | Out-File -Encoding ascii $keyFile
    Write-Host "  Created key pair: $keyFile" -ForegroundColor Green
} else {
    Write-Host "  Key pair exists: $keyName" -ForegroundColor Green
}

# --- Step 4: Launch EC2 Instance ---
Write-Host "[4/5] Launching EC2 instance ($instanceType)..." -ForegroundColor Yellow

# User data script
$userData = @"
#!/bin/bash
yum update -y
yum install -y python3.11 python3.11-pip git cronie
pip3.11 install streamlit pandas plotly openpyxl boto3 requests streamlit-autorefresh
mkdir -p /opt/smartsuite
chown ec2-user:ec2-user /opt/smartsuite

# Setup cron for automation
systemctl enable crond
systemctl start crond

# Create automation cron entry
echo "*/5 * * * * ec2-user cd /opt/smartsuite && /usr/bin/python3.11 automation_cron.py >> /opt/smartsuite/logs/automation.log 2>&1" > /etc/cron.d/smartsuite-automation
chmod 644 /etc/cron.d/smartsuite-automation
"@

$userDataB64 = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($userData))

$instanceId = aws ec2 run-instances `
    --image-id $ami `
    --instance-type $instanceType `
    --key-name $keyName `
    --security-group-ids $sgId `
    --iam-instance-profile "Name=$instanceProfileName" `
    --user-data $userDataB64 `
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=SmartSuite}]" `
    --region $region `
    --query "Instances[0].InstanceId" --output text

Write-Host "  Instance ID: $instanceId" -ForegroundColor Green
Write-Host "  Waiting for instance to be running..." -ForegroundColor Yellow

aws ec2 wait instance-running --instance-ids $instanceId --region $region

# Get IP
$ip = aws ec2 describe-instances --instance-ids $instanceId `
    --query "Reservations[0].Instances[0].PrivateIpAddress" --output text --region $region
$publicIp = aws ec2 describe-instances --instance-ids $instanceId `
    --query "Reservations[0].Instances[0].PublicIpAddress" --output text --region $region

Write-Host "  Private IP: $ip" -ForegroundColor Green
if ($publicIp -and $publicIp -ne "None") {
    Write-Host "  Public IP: $publicIp" -ForegroundColor Green
}

# --- Step 5: Upload code & start ---
Write-Host "[5/5] Waiting 90s for instance initialization..." -ForegroundColor Yellow
Start-Sleep -Seconds 90

Write-Host "  Uploading Smart Suite code..." -ForegroundColor Yellow

# Create temp package
$deployDir = "$env:TEMP\smartsuite_deploy"
if (Test-Path $deployDir) { Remove-Item -Recurse -Force $deployDir }
New-Item -ItemType Directory -Path $deployDir -Force | Out-Null
New-Item -ItemType Directory -Path "$deployDir\ui" -Force | Out-Null
New-Item -ItemType Directory -Path "$deployDir\ui\.streamlit" -Force | Out-Null
New-Item -ItemType Directory -Path "$deployDir\input" -Force | Out-Null
New-Item -ItemType Directory -Path "$deployDir\input\knowledge" -Force | Out-Null
New-Item -ItemType Directory -Path "$deployDir\output" -Force | Out-Null
New-Item -ItemType Directory -Path "$deployDir\logs" -Force | Out-Null

# Copy essential files
Copy-Item "ui\app.py" "$deployDir\ui\" -Force
Copy-Item "ui\engine.py" "$deployDir\ui\" -Force
Copy-Item "ui\app_zhice.py" "$deployDir\ui\" -Force -ErrorAction SilentlyContinue
Copy-Item "ui\.streamlit\*" "$deployDir\ui\.streamlit\" -Force -ErrorAction SilentlyContinue
Copy-Item "automation_cron.py" "$deployDir\" -Force
Copy-Item "input\seo_sem_keywords.csv" "$deployDir\input\" -Force -ErrorAction SilentlyContinue
Copy-Item "input\persona_matrix.json" "$deployDir\input\" -Force -ErrorAction SilentlyContinue
Copy-Item "input\knowledge\*" "$deployDir\input\knowledge\" -Force -ErrorAction SilentlyContinue

# Copy output data (user rules, batch data)
if (Test-Path "output\users.json") { Copy-Item "output\users.json" "$deployDir\output\" -Force }
if (Test-Path "output\requests") { Copy-Item "output\requests" "$deployDir\output\requests" -Recurse -Force }
if (Test-Path "output\batch_001") { Copy-Item "output\batch_001" "$deployDir\output\batch_001" -Recurse -Force }
if (Test-Path "output\batch_002") { Copy-Item "output\batch_002" "$deployDir\output\batch_002" -Recurse -Force }
if (Test-Path "output\batch_003") { Copy-Item "output\batch_003" "$deployDir\output\batch_003" -Recurse -Force }

# SCP upload
$sshOpts = "-o StrictHostKeyChecking=no -o ConnectTimeout=30"
$target = "ec2-user@${ip}"

Write-Host "  Uploading to $target..." -ForegroundColor Yellow
scp $sshOpts -i $keyFile -r "$deployDir\*" "${target}:/opt/smartsuite/"

# Start Streamlit
Write-Host "  Starting Streamlit..." -ForegroundColor Yellow
$startCmd = "cd /opt/smartsuite/ui && nohup python3.11 -m streamlit run app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true > /tmp/streamlit.log 2>&1 &"
ssh $sshOpts -i $keyFile $target $startCmd

Write-Host ""
Write-Host "=== DEPLOYMENT COMPLETE ===" -ForegroundColor Green
Write-Host "Instance ID:  $instanceId" -ForegroundColor Cyan
Write-Host "Private IP:   $ip" -ForegroundColor Cyan
if ($publicIp -and $publicIp -ne "None") {
    Write-Host "Public IP:    $publicIp" -ForegroundColor Cyan
}
Write-Host "Smart Suite:  http://${ip}:8501" -ForegroundColor Green
Write-Host ""
Write-Host "Features enabled:" -ForegroundColor Yellow
Write-Host "  - Streamlit app (port 8501)" -ForegroundColor White
Write-Host "  - Automation cron (every 5 min)" -ForegroundColor White
Write-Host "  - Bedrock access via Instance Profile" -ForegroundColor White
Write-Host ""
Write-Host "SSH Access:   ssh -i $keyFile ec2-user@$ip" -ForegroundColor Gray
Write-Host "Stop:         aws ec2 stop-instances --instance-ids $instanceId --region $region" -ForegroundColor Gray
Write-Host "Terminate:    aws ec2 terminate-instances --instance-ids $instanceId --region $region" -ForegroundColor Gray
