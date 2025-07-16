#!/bin/bash

# Deployment script for AWS Elastic Beanstalk
echo "🚀 Starting deployment to AWS Elastic Beanstalk..."

# Check if EB CLI is installed
if ! command -v eb &> /dev/null; then
    echo "❌ EB CLI not found. Installing..."
    pip install awsebcli
fi

# Check if AWS CLI is configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS CLI not configured. Please run 'aws configure' first."
    exit 1
fi

# Initialize EB application if not already done
if [ ! -f ".elasticbeanstalk/config.yml" ]; then
    echo "📝 Initializing Elastic Beanstalk application..."
    eb init --platform python-3.11 --region us-east-1
fi

# Create deployment package
echo "📦 Creating deployment package..."
rm -rf .ebextensions/__pycache__
rm -rf templates/__pycache__
rm -rf *.pyc

# Deploy to EB
echo "🚀 Deploying to Elastic Beanstalk..."
eb deploy

echo "✅ Deployment completed!"
echo "🌐 Your application should be available at the EB URL" 