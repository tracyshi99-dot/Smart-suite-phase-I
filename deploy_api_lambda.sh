#!/bin/bash
# Smart Suite API → Lambda + API Gateway 部署脚本
# 在 WSL 中运行: bash deploy_api_lambda.sh

set -e

FUNCTION_NAME="smartsuite-api"
ROLE_NAME="smartsuite-lambda-role"
ACCOUNT_ID="830279064391"
REGION="us-east-1"
S3_BUCKET="smartsuite-sync-data"
API_ID="asq6n6kw78"  # 已创建的 API Gateway ID

# 项目路径 (WSL 下的 Windows 路径)
PROJECT_DIR="/mnt/c/Users/yujiashi/Desktop/SmartSuite_Phase1"
TEMP_DIR="/tmp/smartsuite_api_pkg"
ZIP_FILE="/tmp/smartsuite_api.zip"

echo "=== Smart Suite API Lambda Deployment (WSL) ==="

# Step 1: 刷新凭证
echo ""
echo "[1/5] Refreshing AWS credentials..."
ada credentials update --account $ACCOUNT_ID --provider conduit --role IibsAdminAccess-DO-NOT-DELETE --once --profile default 2>/dev/null || echo "  (ada not available, using existing creds)"

# Step 2: 打包
echo ""
echo "[2/5] Packaging Lambda function..."
rm -rf $TEMP_DIR $ZIP_FILE
mkdir -p $TEMP_DIR

# 安装 Python 依赖（Linux 版本，Lambda 兼容）
echo "  Installing dependencies..."
pip3 install fastapi mangum pydantic boto3 pandas requests python-multipart -t $TEMP_DIR --quiet --platform manylinux2014_x86_64 --only-binary=:all: 2>/dev/null || \
pip3 install fastapi mangum pydantic boto3 pandas requests python-multipart -t $TEMP_DIR --quiet

# 复制源代码
echo "  Copying source files..."
cp "$PROJECT_DIR/api/main.py" "$TEMP_DIR/main.py"
cp "$PROJECT_DIR/ui/engine.py" "$TEMP_DIR/engine.py"

# 复制 users.json
mkdir -p "$TEMP_DIR/output"
cp "$PROJECT_DIR/output/users.json" "$TEMP_DIR/output/users.json" 2>/dev/null || echo "  (users.json not found, skipping)"

# 复制 config
mkdir -p "$TEMP_DIR/config/regions"
cp "$PROJECT_DIR/config/regions/"*.json "$TEMP_DIR/config/regions/" 2>/dev/null || true

# 创建 zip
echo "  Creating zip..."
cd $TEMP_DIR
zip -r $ZIP_FILE . -q
cd -

SIZE=$(du -m $ZIP_FILE | cut -f1)
echo "  Package size: ${SIZE}MB"

# Step 3: 上传到 S3（如果 > 50MB）
echo ""
echo "[3/5] Uploading to Lambda..."
if [ "$SIZE" -gt 50 ]; then
    echo "  Package > 50MB, uploading via S3..."
    aws s3 cp $ZIP_FILE "s3://$S3_BUCKET/lambda/smartsuite_api.zip" --profile default
    
    # 检查函数是否存在
    if aws lambda get-function --function-name $FUNCTION_NAME --profile default 2>/dev/null; then
        aws lambda update-function-code \
            --function-name $FUNCTION_NAME \
            --s3-bucket $S3_BUCKET \
            --s3-key "lambda/smartsuite_api.zip" \
            --profile default > /dev/null
    else
        ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/${ROLE_NAME}"
        aws lambda create-function \
            --function-name $FUNCTION_NAME \
            --runtime python3.11 \
            --role $ROLE_ARN \
            --handler "main.handler" \
            --code "S3Bucket=$S3_BUCKET,S3Key=lambda/smartsuite_api.zip" \
            --timeout 120 \
            --memory-size 1024 \
            --environment "Variables={SMARTSUITE_S3_BUCKET=$S3_BUCKET,SMARTSUITE_S3_PREFIX=smartsuite/}" \
            --profile default > /dev/null
    fi
else
    echo "  Direct upload..."
    if aws lambda get-function --function-name $FUNCTION_NAME --profile default 2>/dev/null; then
        aws lambda update-function-code \
            --function-name $FUNCTION_NAME \
            --zip-file "fileb://$ZIP_FILE" \
            --profile default > /dev/null
    else
        ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/${ROLE_NAME}"
        aws lambda create-function \
            --function-name $FUNCTION_NAME \
            --runtime python3.11 \
            --role $ROLE_ARN \
            --handler "main.handler" \
            --zip-file "fileb://$ZIP_FILE" \
            --timeout 120 \
            --memory-size 1024 \
            --environment "Variables={SMARTSUITE_S3_BUCKET=$S3_BUCKET,SMARTSUITE_S3_PREFIX=smartsuite/}" \
            --profile default > /dev/null
    fi
fi
echo "  Lambda deployed!"

# Step 4: 配置
echo ""
echo "[4/5] Updating Lambda configuration..."
sleep 5
PANDAS_LAYER="arn:aws:lambda:${REGION}:336392948345:layer:AWSSDKPandas-Python311:20"
aws lambda update-function-configuration \
    --function-name $FUNCTION_NAME \
    --timeout 120 \
    --memory-size 1024 \
    --handler "main.handler" \
    --layers $PANDAS_LAYER \
    --environment "Variables={SMARTSUITE_S3_BUCKET=$S3_BUCKET,SMARTSUITE_S3_PREFIX=smartsuite/}" \
    --profile default > /dev/null 2>&1 || echo "  (config update pending, may need retry)"
echo "  Configuration updated"

# Step 5: 测试
echo ""
echo "[5/5] Testing API..."
API_URL="https://${API_ID}.execute-api.${REGION}.amazonaws.com"
sleep 3
RESPONSE=$(curl -s "${API_URL}/api/health" 2>/dev/null)
echo "  Health check: $RESPONSE"

echo ""
echo "=== DEPLOYMENT COMPLETE ==="
echo ""
echo "API URL: $API_URL"
echo ""
echo "Next step: Go to Vercel and set environment variable:"
echo "  NEXT_PUBLIC_API_URL = $API_URL"
echo "  URL: https://vercel.com/cngs/smartsuite-geo/settings/environment-variables"
echo ""
