# Smart Suite Lambda Deployment Script
# Prerequisites: AWS CLI configured, ada credentials refreshed
# Account: 830279064391, Region: us-east-1

$FUNCTION_NAME = "smartsuite-automation"
$ROLE_NAME = "smartsuite-lambda-role"
$ACCOUNT_ID = "830279064391"
$REGION = "us-east-1"
$S3_BUCKET = "smartsuite-sync-data"
$SCHEDULE_RATE = "rate(5 minutes)"

Write-Host "=== Smart Suite Lambda Deployment ===" -ForegroundColor Cyan

# Step 1: Refresh credentials
Write-Host "`n[1/6] Refreshing AWS credentials..." -ForegroundColor Yellow
ada credentials update --account $ACCOUNT_ID --provider conduit --role IibsAdminAccess-DO-NOT-DELETE --once --profile default 2>$null

# Step 2: Create IAM Role (skip if exists)
Write-Host "`n[2/6] Creating IAM role..." -ForegroundColor Yellow
$TRUST_POLICY = @"
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"Service": "lambda.amazonaws.com"},
    "Action": "sts:AssumeRole"
  }]
}
"@
$TRUST_FILE = "$env:TEMP\lambda_trust.json"
$TRUST_POLICY | Out-File -FilePath $TRUST_FILE -Encoding utf8

$roleArn = ""
try {
    $roleResult = aws iam get-role --role-name $ROLE_NAME --profile default 2>$null | ConvertFrom-Json
    $roleArn = $roleResult.Role.Arn
    Write-Host "  Role exists: $roleArn"
} catch {
    aws iam create-role --role-name $ROLE_NAME --assume-role-policy-document file://$TRUST_FILE --profile default
    $roleArn = "arn:aws:iam::${ACCOUNT_ID}:role/${ROLE_NAME}"
    Write-Host "  Created role: $roleArn"
    Start-Sleep -Seconds 10  # Wait for role propagation
}

# Attach policies
aws iam attach-role-policy --role-name $ROLE_NAME --policy-arn "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole" --profile default 2>$null
aws iam attach-role-policy --role-name $ROLE_NAME --policy-arn "arn:aws:iam::aws:policy/AmazonS3FullAccess" --profile default 2>$null
Write-Host "  Policies attached (Lambda basic + S3)"

# Step 3: Package Lambda function
Write-Host "`n[3/6] Packaging Lambda function..." -ForegroundColor Yellow
$ZIP_FILE = "$env:TEMP\smartsuite_lambda.zip"
if (Test-Path $ZIP_FILE) { Remove-Item $ZIP_FILE }

# Create package with handler.py + pandas layer reference
Compress-Archive -Path ".\lambda\handler.py" -DestinationPath $ZIP_FILE -Force
Write-Host "  Package created: $ZIP_FILE"

# Step 4: Create/Update Lambda function
Write-Host "`n[4/6] Deploying Lambda function..." -ForegroundColor Yellow
$functionExists = $false
try {
    aws lambda get-function --function-name $FUNCTION_NAME --profile default 2>$null | Out-Null
    $functionExists = $true
} catch {}

if ($functionExists) {
    aws lambda update-function-code `
        --function-name $FUNCTION_NAME `
        --zip-file "fileb://$ZIP_FILE" `
        --profile default
    Write-Host "  Function updated"
} else {
    aws lambda create-function `
        --function-name $FUNCTION_NAME `
        --runtime python3.11 `
        --role $roleArn `
        --handler handler.handler `
        --zip-file "fileb://$ZIP_FILE" `
        --timeout 300 `
        --memory-size 512 `
        --environment "Variables={SMARTSUITE_S3_BUCKET=$S3_BUCKET,SMARTSUITE_S3_PREFIX=smartsuite/}" `
        --profile default
    Write-Host "  Function created"
}

# Step 5: Add pandas layer (AWS managed)
Write-Host "`n[5/6] Adding pandas layer..." -ForegroundColor Yellow
# Use AWS-provided pandas layer for Python 3.11
$PANDAS_LAYER = "arn:aws:lambda:${REGION}:336392948345:layer:AWSSDKPandas-Python311:20"
aws lambda update-function-configuration `
    --function-name $FUNCTION_NAME `
    --layers $PANDAS_LAYER `
    --timeout 300 `
    --memory-size 512 `
    --environment "Variables={SMARTSUITE_S3_BUCKET=$S3_BUCKET,SMARTSUITE_S3_PREFIX=smartsuite/}" `
    --profile default 2>$null
Write-Host "  Layer attached: AWSSDKPandas"

# Step 6: Create EventBridge schedule (every 5 minutes)
Write-Host "`n[6/6] Creating EventBridge schedule..." -ForegroundColor Yellow
$RULE_NAME_EB = "smartsuite-automation-schedule"

aws events put-rule `
    --name $RULE_NAME_EB `
    --schedule-expression $SCHEDULE_RATE `
    --state ENABLED `
    --profile default 2>$null

# Add Lambda permission for EventBridge
aws lambda add-permission `
    --function-name $FUNCTION_NAME `
    --statement-id "EventBridgeInvoke" `
    --action "lambda:InvokeFunction" `
    --principal "events.amazonaws.com" `
    --source-arn "arn:aws:events:${REGION}:${ACCOUNT_ID}:rule/${RULE_NAME_EB}" `
    --profile default 2>$null

# Add target
$TARGET_JSON = @"
[{"Id": "smartsuite-lambda-target", "Arn": "arn:aws:lambda:${REGION}:${ACCOUNT_ID}:function:${FUNCTION_NAME}"}]
"@
$TARGET_FILE = "$env:TEMP\lambda_target.json"
$TARGET_JSON | Out-File -FilePath $TARGET_FILE -Encoding utf8

aws events put-targets `
    --rule $RULE_NAME_EB `
    --targets file://$TARGET_FILE `
    --profile default 2>$null

Write-Host "`n=== Deployment Complete ===" -ForegroundColor Green
Write-Host "Function: $FUNCTION_NAME"
Write-Host "Schedule: Every 5 minutes (EventBridge)"
Write-Host "S3 Bucket: $S3_BUCKET"
Write-Host "Memory: 512MB, Timeout: 300s"
Write-Host "`nTo test manually:"
Write-Host "  aws lambda invoke --function-name $FUNCTION_NAME --profile default /tmp/response.json"
