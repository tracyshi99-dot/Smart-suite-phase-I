#!/bin/bash
# Run this on EC2 after upload to fix line endings and start services

# Fix Windows line endings on all Python files
find /opt/smartsuite -name "*.py" -exec sed -i 's/\r$//' {} \;
find /opt/smartsuite -name "*.toml" -exec sed -i 's/\r$//' {} \;
find /opt/smartsuite -name "*.csv" -exec sed -i 's/\r$//' {} \;

# Install dependencies
sudo pip3.11 install streamlit pandas plotly openpyxl boto3 requests streamlit-autorefresh 2>/dev/null || \
sudo python3.11 -m pip install streamlit pandas plotly openpyxl boto3 requests streamlit-autorefresh

# Create logs dir
mkdir -p /opt/smartsuite/logs

# Setup cron for automation (every 5 min)
echo '*/5 * * * * ec2-user cd /opt/smartsuite && /usr/bin/python3.11 automation_cron.py >> /opt/smartsuite/logs/automation.log 2>&1' | sudo tee /etc/cron.d/smartsuite-automation > /dev/null
sudo chmod 644 /etc/cron.d/smartsuite-automation
sudo systemctl restart crond 2>/dev/null || sudo systemctl restart cron 2>/dev/null

# Kill existing streamlit if any
pkill -f "streamlit run" 2>/dev/null
sleep 2

# Start Streamlit
cd /opt/smartsuite/ui
nohup python3.11 -m streamlit run app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true > /tmp/streamlit.log 2>&1 &

echo ""
echo "=== Setup Complete ==="
echo "Streamlit PID: $(pgrep -f 'streamlit run')"
echo "Cron configured: every 5 min"
echo "Access: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):8501"
