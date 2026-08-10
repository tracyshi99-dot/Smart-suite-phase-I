# Smart Suite API Lambda + API Gateway Deployment
# Deploys api/main.py as a Lambda function behind HTTP API Gateway
# Prerequisites: AWS CLI configured, ada credentials

$FUNCTION_NAME = "smartsuite-api"
$ROLE_NAME = "smartsuite-lambda-role"
$ACCOUNT_ID = "830279064391"
$REGION = "us-east-1"
$S3_BUCKET = "smartsuite-sync-data"
$API_NAME = "smartsuite-http-api"

Write-Host "=== Smart Suite API Lambda Deployment ===" -ForegroundColor Cyan

# Step 1: Refresh credentials
Write-Host "`n[1/7] Refreshing AWS credentials..." -ForegroundColor Yellow
ada credentials update --account $ACCOUNT_ID --provider conduit --role IibsAdminAccess-DO-NOT-DELETE --once --profile default 2>$null

# Step 2: Ensure IAM Role exists
Write-Host "`n[2/7] Checking IAM role..." -ForegroundColor Yellow
$roleArn = "arn:aws:iam::${ACCOUNT_ID}:role/${ROLE_NAME}"
try {
    aws iam get-role --role-name $ROLE_NAME --profile default 2>$null | Out-Null
    Write-Host "  Role exists: $roleArn"
} catch {
    Write-Host "  Role not found. Please run deploy_lambda.ps1 first to create it."
    exit 1
}

# Step 3: Package Lambda function
Write-Host "`n[3/7] Packaging Lambda function..." -ForegroundColor Yellow
$PACKAGE_DIR = "$env:TEMP\smartsuite_api_package"
$ZIP_FILE = "$env:TEMP\smartsuite_api.zip"

# Clean
if (Test-Path $PACKAGE_DIR) { Remove-Item -Recurse -Force $PACKAGE_DIR }
if (Test-Path $ZIP_FILE) { Remove-Item $ZIP_FILE }

New-Item -ItemType Directory -Path $PACKAGE_DIR | Out-Null

# Install dependencies
Write-Host "  Installing dependencies..."
pip install fastapi mangum pydantic boto3 pandas requests python-multipart -t $PACKAGE_DIR --quiet 2>$null

# Copy API code
Write-Host "  Copying API code..."
Copy-Item "api\main.py" "$PACKAGE_DIR\main.py"
Copy-Item "api\__init__.py" "$PACKAGE_DIR\__init__.py" -ErrorAction SilentlyContinue

# Copy engine.py (needed for actual operations)
Copy-Item "ui\engine.py" "$PACKAGE_DIR\engine.py"

# Copy config and data files needed
if (Test-Path "output\users.json") {
    New-Item -ItemType Directory -Path "$PACKAGE_DIR\output" -Force | Out-Null
    Copy-Item "output\users.json" "$PACKAGE_DIR\output\users.json"
}

# Create zip
Write-Host "  Creating zip package..."
Compress-Archive -Path "$PACKAGE_DIR\*" -DestinationPath $ZIP_FILE -Force

$zipSize = (Get-Item $ZIP_FILE).Length / 1MB
Write-Host "  Package size: $([math]::Round($zipSize, 1)) MB"

# If package > 50MB, upload to S3 first
if ($zipSize -gt 50) {
    Write-Host "  Package too large for direct upload, using S3..."
    aws s3 cp $ZIP_FILE "s3://$S3_BUCKET/lambda/smartsuite_api.zip" --profile default
    $S3_CODE = "--s3-bucket $S3_BUCKET --s3-key lambda/smartsuite_api.zip"
} else {
    $S3_CODE = ""
}

# Step 4: Create/Update Lambda function
Write-Host "`n[4/7] Deploying Lambda function..." -ForegroundColor Yellow
$functionExists = $false
try {
    aws lambda get-function --function-name $FUNCTION_NAME --profile default 2>$null | Out-Null
    $functionExists = $true
} catch {}

$ENV_VARS = "Variables={SMARTSUITE_S3_BUCKET=$S3_BUCKET,SMARTSUITE_S3_PREFIX=smartsuite/,PYTHONPATH=/var/task}"

if ($functionExists) {
    if ($S3_CODE) {
        aws lambda update-function-code --function-name $FUNCTION_NAME --s3-bucket $S3_BUCKET --s3-key "lambda/smartsuite_api.zip" --profile default | Out-Null
    } else {
        aws lambda update-function-code --function-name $FUNCTION_NAME --zip-file "fileb://$ZIP_FILE" --profile default | Out-Null
    }
    Start-Sleep -Seconds 5
    aws lambda update-function-configuration --function-name $FUNCTION_NAME --timeout 120 --memory-size 1024 --environment $ENV_VARS --handler "main.handler" --profile default | Out-Null
    Write-Host "  Function updated"
} else {
    if ($S3_CODE) {
        aws lambda create-function --function-name $FUNCTION_NAME --runtime python3.11 --role $roleArn --handler "main.handler" --code "S3Bucket=$S3_BUCKET,S3Key=lambda/smartsuite_api.zip" --timeout 120 --memory-size 1024 --environment $ENV_VARS --profile default | Out-Null
    } else {
        aws lambda create-function --function-name $FUNCTION_NAME --runtime python3.11 --role $roleArn --handler "main.handler" --zip-file "fileb://$ZIP_FILE" --timeout 120 --memory-size 1024 --environment $ENV_VARS --profile default | Out-Null
    }
    Write-Host "  Function created"
    Start-Sleep -Seconds 5
}

# Step 5: Add pandas layer
Write-Host "`n[5/7] Adding pandas layer..." -ForegroundColor Yellow
$PANDAS_LAYER = "arn:aws:lambda:${REGION}:336392948345:layer:AWSSDKPandas-Python311:20"
aws lambda update-function-configuration --function-name $FUNCTION_NAME --layers $PANDAS_LAYER --profile default 2>$null | Out-Null
Write-Host "  Layer attached"

# Step 6: Create HTTP API Gateway
Write-Host "`n[6/7] Creating HTTP API Gateway..." -ForegroundColor Yellow

# Check if API already exists
$apiId = ""
$apis = aws apigatewayv2 get-apis --profile default 2>$null | ConvertFrom-Json
foreach ($api in $apis.Items) {
    if ($api.Name -eq $API_NAME) {
        $apiId = $api.ApiId
        break
    }
}

if (-not $apiId) {
    # Create new HTTP API
    $createResult = aws apigatewayv2 create-api --name $API_NAME --protocol-type HTTP --cors-configuration "AllowOrigins=https://smartsuite-geo.vercel.app,https://geo-smartsuite.app,http://localhost:3000,AllowMethods=*,AllowHeaders=*" --profile default | ConvertFrom-Json
    $apiId = $createResult.ApiId
    Write-Host "  API created: $apiId"
} else {
    Write-Host "  API exists: $apiId"
}

# Create Lambda integration
$integrationId = ""
$integrations = aws apigatewayv2 get-integrations --api-id $apiId --profile default 2>$null | ConvertFrom-Json
if ($integrations.Items.Count -gt 0) {
    $integrationId = $integrations.Items[0].IntegrationId
    Write-Host "  Integration exists: $integrationId"
} else {
    $lambdaArn = "arn:aws:lambda:${REGION}:${ACCOUNT_ID}:function:${FUNCTION_NAME}"
    $intResult = aws apigatewayv2 create-integration --api-id $apiId --integration-type AWS_PROXY --integration-uri $lambdaArn --payload-format-version "2.0" --profile default | ConvertFrom-Json
    $integrationId = $intResult.IntegrationId
    Write-Host "  Integration created: $integrationId"
}

# Create catch-all route
$routes = aws apigatewayv2 get-routes --api-id $apiId --profile default 2>$null | ConvertFrom-Json
if ($routes.Items.Count -eq 0) {
    aws apigatewayv2 create-route --api-id $apiId --route-key "`$default" --target "integrations/$integrationId" --profile default | Out-Null
    Write-Host "  Route created: `$default"
} else {
    Write-Host "  Route exists"
}

# Create/update stage
$stages = aws apigatewayv2 get-stages --api-id $apiId --profile default 2>$null | ConvertFrom-Json
$hasDefault = $false
foreach ($stage in $stages.Items) {
    if ($stage.StageName -eq "`$default") { $hasDefault = $true }
}
if (-not $hasDefault) {
    aws apigatewayv2 create-stage --api-id $apiId --stage-name "`$default" --auto-deploy --profile default | Out-Null
    Write-Host "  Stage created: `$default (auto-deploy)"
}

# Step 7: Add Lambda invoke permission for API Gateway
Write-Host "`n[7/7] Setting permissions..." -ForegroundColor Yellow
aws lambda add-permission --function-name $FUNCTION_NAME --statement-id "apigateway-invoke" --action "lambda:InvokeFunction" --principal "apigateway.amazonaws.com" --source-arn "arn:aws:execute-api:${REGION}:${ACCOUNT_ID}:${apiId}/*" --profile default 2>$null

$API_URL = "https://${apiId}.execute-api.${REGION}.amazonaws.com"

Write-Host "`n=== Deployment Complete ===" -ForegroundColor Green
Write-Host "Lambda Function: $FUNCTION_NAME" -ForegroundColor White
Write-Host "API Gateway URL: $API_URL" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Test: curl $API_URL/api/health"
Write-Host "2. Set Vercel env var: NEXT_PUBLIC_API_URL = $API_URL"
Write-Host "   (Go to: vercel.com/cngs/smartsuite-geo/settings/environment-variables)"
Write-Host ""

# Save URL to file for reference
"$API_URL" | Out-File -FilePath "api_gateway_url.txt" -Encoding utf8
Write-Host "API URL saved to api_gateway_url.txt"
