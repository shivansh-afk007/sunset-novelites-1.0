#!/bin/bash

# AWS CLI Configuration Script
echo "🔧 Setting up AWS CLI for new account..."

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not installed. Please install it first:"
    echo "   Windows: https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2-windows.html"
    echo "   Linux/Mac: pip install awscli"
    exit 1
fi

echo "📝 Please provide your AWS credentials:"
echo "   You can get these from your AWS Console > IAM > Users > Security credentials"

# Configure AWS CLI
echo "🔑 Configuring AWS CLI..."
aws configure

# Test the configuration
echo "🧪 Testing AWS configuration..."
if aws sts get-caller-identity &> /dev/null; then
    echo "✅ AWS CLI configured successfully!"
    echo "📊 Account information:"
    aws sts get-caller-identity
else
    echo "❌ AWS CLI configuration failed. Please check your credentials."
    exit 1
fi

# Install EB CLI
echo "📦 Installing Elastic Beanstalk CLI..."
pip install awsebcli

echo "✅ Setup completed! You can now deploy with: ./deploy_to_eb.sh" 