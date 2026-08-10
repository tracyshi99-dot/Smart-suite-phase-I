#!/bin/bash
# ============================================
# 在 WSL 终端里直接粘贴运行这整段脚本
# 它会：1) 打包 fastapi layer  2) 上传 S3  3) 创建 Layer  4) 绑定到 Lambda  5) 测试
# ============================================

echo "=== Step 1: 打包 fastapi + mangum Layer ==="
rm -rf /tmp/layer /tmp/fastapi_layer.zip
mkdir -p /tmp/layer/python

pip3 install fastapi mangum pydantic requests python-multipart -t /tmp/layer/python --quiet 2>/dev/null
echo "  Dependencies installed"

cd /tmp/layer
zip -r /tmp/fastapi_layer.zip python/ -q
SIZE=$(du -m /tmp/fastapi_layer.zip | cut -f1)
echo "  Layer zip: ${SIZE}MB"

# 复制到 Windows 供 aws cli 使用
cp /tmp/fastapi_layer.zip /mnt/c/Users/yujiashi/Desktop/SmartSuite_Phase1/fastapi_layer.zip
echo "  Copied to project root"

echo ""
echo "=== Step 2: 上传到 S3 ==="
cd /mnt/c/Users/yujiashi/Desktop/SmartSuite_Phase1

# 尝试用 Windows aws cli (通过 cmd.exe)
cmd.exe /c "aws s3 cp fastapi_layer.zip s3://smartsuite-sync-data/lambda/fastapi_layer.zip --profile default" 2>/dev/null
echo "  Uploaded to S3"

echo ""
echo "=== Step 3: 创建 Lambda Layer ==="
LAYER_OUTPUT=$(cmd.exe /c "aws lambda publish-layer-version --layer-name fastapi-mangum --compatible-runtimes python3.11 --content S3Bucket=smartsuite-sync-data,S3Key=lambda/fastapi_layer.zip --profile default" 2>/dev/null)
echo "$LAYER_OUTPUT"

# 提取 LayerVersionArn
LAYER_ARN=$(echo "$LAYER_OUTPUT" | grep -o '"LayerVersionArn": "[^"]*"' | cut -d'"' -f4)
echo "  Layer ARN: $LAYER_ARN"

echo ""
echo "=== Step 4: 绑定 Layer 到 Lambda 函数 ==="
PANDAS_LAYER="arn:aws:lambda:us-east-1:336392948345:layer:AWSSDKPandas-Python311:20"

if [ -n "$LAYER_ARN" ]; then
    cmd.exe /c "aws lambda update-function-configuration --function-name smartsuite-api --layers $PANDAS_LAYER $LAYER_ARN --profile default" 2>/dev/null | head -5
    echo "  Layers attached!"
else
    echo "  ERROR: Layer ARN not found. Run manually:"
    echo "  aws lambda update-function-configuration --function-name smartsuite-api --layers $PANDAS_LAYER arn:aws:lambda:us-east-1:830279064391:layer:fastapi-mangum:1 --profile default"
fi

echo ""
echo "=== Step 5: 等待并测试 ==="
sleep 8
RESPONSE=$(curl -s "https://asq6n6kw78.execute-api.us-east-1.amazonaws.com/api/health")
echo "  Health check response: $RESPONSE"

echo ""
echo "============================================"
echo "完成！"
echo ""
echo "API URL: https://asq6n6kw78.execute-api.us-east-1.amazonaws.com"
echo ""
echo "最后一步：去 Vercel 设置环境变量"
echo "  网址: https://vercel.com/cngs/smartsuite-geo/settings/environment-variables"
echo "  Key:   NEXT_PUBLIC_API_URL"
echo "  Value: https://asq6n6kw78.execute-api.us-east-1.amazonaws.com"
echo "  然后点 Save，Vercel 会自动重新部署"
echo "============================================"
