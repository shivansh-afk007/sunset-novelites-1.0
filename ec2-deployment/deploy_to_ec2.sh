#!/bin/bash

# EC2 Instance Deployment Script for Flask Dashboard
# Instance IP: 13.60.229.228

echo "🚀 Starting EC2 deployment..."

# Update system
sudo yum update -y

# Install Python 3 and pip
sudo yum install -y python3 python3-pip git

# Install additional dependencies
sudo yum install -y gcc python3-devel

# Create application directory
sudo mkdir -p /opt/dashboard
sudo chown ec2-user:ec2-user /opt/dashboard

# Copy application files (this will be done via SCP)
echo "📁 Application directory created at /opt/dashboard"

# Create virtual environment
cd /opt/dashboard
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install flask mysql-connector-python pandas numpy plotly

# Create systemd service file
sudo tee /etc/systemd/system/dashboard.service > /dev/null <<EOF
[Unit]
Description=Dashboard Flask Application
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/opt/dashboard
Environment=PATH=/opt/dashboard/venv/bin
ExecStart=/opt/dashboard/venv/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start the service
sudo systemctl daemon-reload
sudo systemctl enable dashboard
sudo systemctl start dashboard

echo "✅ Dashboard service created and started"
echo "🌐 Application should be available at: http://13.60.229.228:5000" 