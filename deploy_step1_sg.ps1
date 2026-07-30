# Step 1: Create Security Group
$region = "us-east-1"
$vpc = "vpc-0e0a085e7870849d5"

$sg = aws ec2 create-security-group `
    --group-name smartsuite-web `
    --description "SmartSuite Streamlit" `
    --vpc-id $vpc `
    --region $region `
    --query GroupId --output text

Write-Host "Security Group ID: $sg"

# Open port 8501 (Streamlit) to internal network
aws ec2 authorize-security-group-ingress --group-id $sg --protocol tcp --port 8501 --cidr 10.0.0.0/8 --region $region | Out-Null
# Open port 22 (SSH) to internal network
aws ec2 authorize-security-group-ingress --group-id $sg --protocol tcp --port 22 --cidr 10.0.0.0/8 --region $region | Out-Null

Write-Host "Ports 22, 8501 opened to 10.0.0.0/8"
Write-Host "SG=$sg" | Out-File -FilePath ".\deploy_state.txt" -Encoding utf8
