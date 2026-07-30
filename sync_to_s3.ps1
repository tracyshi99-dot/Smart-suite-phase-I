# Sync local data to S3 (run once to seed the bucket)
Write-Host "Syncing output/ to S3..." -ForegroundColor Yellow
aws s3 sync output/ s3://smartsuite-sync-data/smartsuite/output/ --region us-east-1 --exclude "*.pptx" --exclude "*.docx" --exclude "*.xlsx"
Write-Host ""
Write-Host "Syncing input/ to S3..." -ForegroundColor Yellow
aws s3 sync input/ s3://smartsuite-sync-data/smartsuite/input/ --region us-east-1
Write-Host ""
Write-Host "Done! S3 bucket seeded." -ForegroundColor Green
aws s3 ls s3://smartsuite-sync-data/smartsuite/ --region us-east-1
