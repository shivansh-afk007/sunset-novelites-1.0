# AWS Elastic Beanstalk Deployment Guide

## Prerequisites

1. **AWS Account**: You need an active AWS account
2. **AWS CLI**: Install AWS CLI v2
3. **Python**: Python 3.11 or later
4. **Git**: For version control

## Step 1: Install AWS CLI

### Windows:
```bash
# Download from: https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2-windows.html
```

### Linux/Mac:
```bash
pip install awscli
```

## Step 2: Configure AWS CLI

Run the setup script:
```bash
chmod +x setup_aws_cli.sh
./setup_aws_cli.sh
```

Or manually configure:
```bash
aws configure
```

You'll need:
- **AWS Access Key ID**: From AWS Console > IAM > Users > Security credentials
- **AWS Secret Access Key**: From the same location
- **Default region**: Choose your preferred region (e.g., us-east-1)
- **Default output format**: json

## Step 3: Install EB CLI

```bash
pip install awsebcli
```

## Step 4: Initialize Elastic Beanstalk

```bash
eb init
```

Choose:
- **Platform**: Python 3.11
- **Region**: Your preferred region
- **Application name**: dashboard-lightpseed
- **Environment name**: dashboard-prod

## Step 5: Deploy

### Option 1: Use the deployment script
```bash
chmod +x deploy_to_eb.sh
./deploy_to_eb.sh
```

### Option 2: Manual deployment
```bash
eb deploy
```

## Step 6: Monitor Deployment

```bash
eb status
eb logs
```

## Step 7: Open Application

```bash
eb open
```

## Troubleshooting

### Common Issues:

1. **Permission Denied**: Make sure your AWS credentials have EB permissions
2. **Memory Issues**: The app uses a lot of memory. Consider upgrading instance type
3. **Timeout Issues**: Database queries can be slow. Consider adding caching

### Useful Commands:

```bash
# View logs
eb logs

# SSH into instance
eb ssh

# Check status
eb status

# List environments
eb list

# Terminate environment
eb terminate
```

## Environment Variables

The application uses these environment variables:
- `RDS_HOST`: Your RDS endpoint
- `RDS_USER`: Database username
- `RDS_PASSWORD`: Database password
- `RDS_DATABASE`: Database name

## Security Notes

1. **Database Security**: Ensure RDS security group allows EB instances
2. **IAM Permissions**: User needs EB, EC2, and RDS permissions
3. **SSL**: Consider adding SSL certificate for production

## Cost Optimization

1. **Instance Type**: Start with t3.micro for testing
2. **Auto Scaling**: Configure based on traffic
3. **RDS**: Use Multi-AZ for production

## Monitoring

1. **CloudWatch**: Monitor application metrics
2. **EB Health**: Check environment health
3. **RDS Monitoring**: Monitor database performance 