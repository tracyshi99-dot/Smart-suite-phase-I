$region = "us-east-1"
$vpc = "vpc-0e0a085e7870849d5"
$subnet = "subnet-065c84b35307cfd55"

Write-Host "Creating security group..."
$sg = aws ec2 create-security-group --group-name smartsuite-sg --description "SmartSuite Streamlit" --vpc-id $vpc --region $region --query GroupId --output text 2>&1
Write-Host "SG: $sg"

Write-Host "Opening ports 8501-8503..."
aws ec2 authorize-security-group-ingress --group-id $sg --protocol tcp --port 8501 --cidr 0.0.0.0/0 --region $region 2>&1 | Out-Null
aws ec2 authorize-security-group-ingress --group-id $sg --protocol tcp --port 8502 --cidr 0.0.0.0/0 --region $region 2>&1 | Out-Null
aws ec2 authorize-security-group-ingress --group-id $sg --protocol tcp --port 8503 --cidr 0.0.0.0/0 --region $region 2>&1 | Out-Null
aws ec2 authorize-security-group-ingress --group-id $sg --protocol tcp --port 22 --cidr 0.0.0.0/0 --region $region 2>&1 | Out-Null

Write-Host "Launching EC2 instance..."
$instance = aws ec2 run-instances --image-id ami-0c02fb55956c7d316 --instance-type t3.small --subnet-id $subnet --security-group-ids $sg --region $region --query "Instances[0].InstanceId" --output text 2>&1
Write-Host "Instance: $instance"

Write-Host "Waiting for instance to be running..."
aws ec2 wait instance-running --instance-ids $instance --region $region 2>&1

$ip = aws ec2 describe-instances --instance-ids $instance --query "Reservations[0].Instances[0].PrivateIpAddress" --output text --region $region 2>&1
Write-Host "Private IP: $ip"
Write-Host "Access URL: http://${ip}:8501"
Write-Host "Done!"
