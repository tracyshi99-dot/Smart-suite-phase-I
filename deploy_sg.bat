@echo off
aws ec2 create-security-group --group-name smartsuite-web --description "SmartSuite Streamlit" --vpc-id vpc-0e0a085e7870849d5 --region us-east-1 --query GroupId --output text > sg_id.txt
type sg_id.txt
aws ec2 authorize-security-group-ingress --group-id /p sg_id.txt --protocol tcp --port 8501 --cidr 10.0.0.0/8 --region us-east-1
aws ec2 authorize-security-group-ingress --group-id /p sg_id.txt --protocol tcp --port 22 --cidr 10.0.0.0/8 --region us-east-1
echo Done
