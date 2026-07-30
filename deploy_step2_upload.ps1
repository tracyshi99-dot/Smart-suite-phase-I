# ============================================================
# Step 2: Upload code & start services on EC2
# Run this after deploy_smartsuite.ps1 succeeds
# ============================================================

$region = "us-east-1"
$instanceId = "i-03ef9211fd81f7c0b"
$ip = "54.196.13.159"  # Use public IP
$keyFile = "$env:USERPROFILE\.ssh\smartsuite-deploy-key.pem"

Write-Host "=== Upload & Configure SmartSuite on EC2 ===" -ForegroundColor Cyan

# --- Open port 8501 to 0.0.0.0/0 (for easy access) ---
Write-Host "[1/4] Opening port 8501 to all..." -ForegroundColor Yellow
aws ec2 authorize-security-group-ingress --group-id sg-08ebc83436fa2d89c --ip-permissions "IpProtocol=tcp,FromPort=8501,ToPort=8501,IpRanges=[{CidrIp=0.0.0.0/0}]" --region $region 2>&1 | Out-Null
Write-Host "  Done" -ForegroundColor Green

# --- Test SSH connection ---
Write-Host "[2/4] Testing SSH connection..." -ForegroundColor Yellow
ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 -i $keyFile ec2-user@$ip "echo 'SSH OK'"
if ($LASTEXITCODE -ne 0) {
    Write-Host "  SSH failed! Check security group or wait for instance to fully boot." -ForegroundColor Red
    exit 1
}
Write-Host "  SSH connected!" -ForegroundColor Green

# --- Upload code ---
Write-Host "[3/4] Packaging and uploading code..." -ForegroundColor Yellow

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
if (Test-Path "ui\app_zhice.py") { Copy-Item "ui\app_zhice.py" "$deployDir\ui\" -Force }
if (Test-Path "ui\simulate_tab.py") { Copy-Item "ui\simulate_tab.py" "$deployDir\ui\" -Force }
if (Test-Path "ui\zhice_engine.py") { Copy-Item "ui\zhice_engine.py" "$deployDir\ui\" -Force }
if (Test-Path "ui\demo_data.py") { Copy-Item "ui\demo_data.py" "$deployDir\ui\" -Force }
if (Test-Path "ui\.streamlit") { Copy-Item "ui\.streamlit\*" "$deployDir\ui\.streamlit\" -Force -ErrorAction SilentlyContinue }
Copy-Item "automation_cron.py" "$deployDir\" -Force
if (Test-Path "input\seo_sem_keywords.csv") { Copy-Item "input\seo_sem_keywords.csv" "$deployDir\input\" -Force }
if (Test-Path "input\persona_matrix.json") { Copy-Item "input\persona_matrix.json" "$deployDir\input\" -Force }
if (Test-Path "input\knowledge") { Copy-Item "input\knowledge\*" "$deployDir\input\knowledge\" -Force -ErrorAction SilentlyContinue }

# Copy output data
if (Test-Path "output\users.json") { Copy-Item "output\users.json" "$deployDir\output\" -Force }
if (Test-Path "output\requests") { Copy-Item "output\requests" "$deployDir\output\requests" -Recurse -Force }
if (Test-Path "output\batch_001") { Copy-Item "output\batch_001" "$deployDir\output\batch_001" -Recurse -Force }
if (Test-Path "output\batch_002") { Copy-Item "output\batch_002" "$deployDir\output\batch_002" -Recurse -Force }
if (Test-Path "output\batch_003") { Copy-Item "output\batch_003" "$deployDir\output\batch_003" -Recurse -Force }

Write-Host "  Uploading via SCP (this may take 1-2 min)..." -ForegroundColor Yellow
scp -o StrictHostKeyChecking=no -i $keyFile -r "$deployDir\*" "ec2-user@${ip}:/opt/smartsuite/"
if ($LASTEXITCODE -ne 0) {
    Write-Host "  SCP failed!" -ForegroundColor Red
    exit 1
}
Write-Host "  Upload complete!" -ForegroundColor Green

# --- Start services ---
Write-Host "[4/4] Starting Streamlit + Cron..." -ForegroundColor Yellow

$setupCmd = @'
# Install dependencies
sudo pip3.11 install streamlit pandas plotly openpyxl boto3 requests streamlit-autorefresh 2>/dev/null

# Create logs dir
mkdir -p /opt/smartsuite/logs

# Setup cron for automation (every 5 min)
echo "*/5 * * * * ec2-user cd /opt/smartsuite && /usr/bin/python3.11 automation_cron.py >> /opt/smartsuite/logs/automation.log 2>&1" | sudo tee /etc/cron.d/smartsuite-automation > /dev/null
sudo chmod 644 /etc/cron.d/smartsuite-automation
sudo systemctl restart crond 2>/dev/null || sudo systemctl restart cron 2>/dev/null

# Kill existing streamlit if any
pkill -f "streamlit run" 2>/dev/null

# Start Streamlit
cd /opt/smartsuite/ui && nohup python3.11 -m streamlit run app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true > /tmp/streamlit.log 2>&1 &

echo "Services started!"
'@

ssh -o StrictHostKeyChecking=no -i $keyFile ec2-user@$ip $setupCmd

Write-Host ""
Write-Host "=== ALL DONE ===" -ForegroundColor Green
Write-Host ""
Write-Host "Smart Suite URL: http://${ip}:8501" -ForegroundColor Cyan
Write-Host ""
Write-Host "Features:" -ForegroundColor Yellow
Write-Host "  [x] Streamlit app running on port 8501" -ForegroundColor White
Write-Host "  [x] Automation cron: every 5 min checks all users' rules" -ForegroundColor White
Write-Host "  [x] Bedrock access via Instance Profile (never expires)" -ForegroundColor White
Write-Host ""
Write-Host "Management:" -ForegroundColor Yellow
Write-Host "  SSH:       ssh -o StrictHostKeyChecking=no -i $keyFile ec2-user@$ip" -ForegroundColor Gray
Write-Host "  Logs:      ssh ... 'cat /tmp/streamlit.log'" -ForegroundColor Gray
Write-Host "  Stop:      aws ec2 stop-instances --instance-ids $instanceId --region $region" -ForegroundColor Gray
Write-Host "  Terminate: aws ec2 terminate-instances --instance-ids $instanceId --region $region" -ForegroundColor Gray
