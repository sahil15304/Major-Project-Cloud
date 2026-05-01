# AWS Deployment Guide

Complete guide for deploying the PPMI Backend API on AWS.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [EC2 Deployment](#ec2-deployment)
3. [S3 Model Storage](#s3-model-storage)
4. [Load Balancing](#load-balancing)
5. [Auto-Scaling](#auto-scaling)
6. [Monitoring](#monitoring)
7. [Cost Estimation](#cost-estimation)
8. [Security](#security)

## Prerequisites

- AWS Account with appropriate IAM permissions
- EC2 instance (Amazon Linux 2, Ubuntu 20.04+, or similar)
- Security group configured with:
  - Port 8000 open (or 80/443 if using load balancer)
  - SSH access (port 22)
- S3 bucket for models (optional but recommended)
- CloudWatch for monitoring (included with AWS)

## EC2 Deployment

### Step 1: Create EC2 Instance

1. **Go to AWS EC2 Console**
   - https://console.aws.amazon.com/ec2

2. **Launch Instance**
   - Click "Launch Instances"
   - Choose AMI: Amazon Linux 2 or Ubuntu 20.04 LTS
   - Instance type: t3.medium (minimum recommended)
   - Storage: 20 GB (root volume)

3. **Configure Security Group**
   - Allow SSH (22): Your IP
   - Allow HTTP (80): 0.0.0.0/0
   - Allow custom port 8000: For testing

4. **Add IAM Role** (if using S3)
   - Create role: EC2 → AmazonS3ReadOnlyAccess
   - Attach to instance

### Step 2: Connect and Setup

```bash
# SSH into instance
ssh -i your-key.pem ec2-user@your-instance-ip

# Update system
sudo yum update -y

# Install Python and build tools
sudo yum install python3 python3-pip -y
sudo yum install gcc python3-devel -y
```

### Step 3: Deploy Application

```bash
# Clone repository
git clone https://your-repo.git
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start server with gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 main:app
```

### Step 4: Setup Systemd Service (For Production)

For production deployments, use systemd to automatically restart the API:

```bash
sudo nano /etc/systemd/system/ppmi-api.service
```

Paste:
```ini
[Unit]
Description=PPMI Parkinson API
After=network.target

[Service]
Type=notify
User=ec2-user
WorkingDirectory=/opt/ppmi-backend/backend
Environment="PATH=/opt/ppmi-backend/backend/venv/bin"
ExecStart=/opt/ppmi-backend/backend/venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable ppmi-api
sudo systemctl start ppmi-api
sudo systemctl status ppmi-api
```

## S3 Model Storage

### Upload Models to S3

```bash
# Create S3 bucket
aws s3 mb s3://ppmi-models-prod --region us-east-1

# Upload models
aws s3 cp xgb_sev_6m.joblib s3://ppmi-models-prod/models/
aws s3 cp xgb_sev_12m.joblib s3://ppmi-models-prod/models/
aws s3 cp xgb_sev_24m.joblib s3://ppmi-models-prod/models/

# Verify
aws s3 ls s3://ppmi-models-prod/models/
```

### Configure S3 Access

1. **Create IAM Role for EC2**
   ```
   Service: EC2
   Policy: AmazonS3ReadOnlyAccess
   ```

2. **Set Environment Variables**
   ```bash
   export MODELS_SOURCE=s3
   export AWS_S3_BUCKET=ppmi-models-prod
   export AWS_S3_MODELS_PREFIX=models/
   export AWS_REGION=us-east-1
   export USE_IAM_ROLE=true
   ```

3. **Restart Application**
   ```bash
   sudo systemctl restart ppmi-api
   ```

### Enable S3 Auto-Download (Optional)

Add to `app/models.py` for automatic S3 model loading:

```python
import boto3
from botocore.config import Config

def load_from_s3(bucket: str, prefix: str, region: str):
    """Load models from S3"""
    s3_client = boto3.client('s3', region_name=region, config=Config(
        signature_version='s3v4',
        retries={'max_attempts': 3}
    ))
    
    models_data = {}
    for model_name in ['severity_6m', 'severity_12m', 'severity_24m']:
        key = f"{prefix}{model_name}.joblib"
        try:
            s3_client.download_file(bucket, key, f'/tmp/{model_name}.joblib')
            models_data[model_name] = joblib.load(f'/tmp/{model_name}.joblib')
        except Exception as e:
            logger.error(f"Error loading {model_name} from S3: {e}")
    
    return models_data
```

## Load Balancing

### Using AWS Application Load Balancer (ALB)

1. **Create Target Group**
   - Go to EC2 → Target Groups
   - Protocol: HTTP, Port: 8000
   - Health check path: `/api/health`
   - Interval: 30s, Timeout: 5s

2. **Create Load Balancer**
   - Go to EC2 → Load Balancers
   - Create Application Load Balancer
   - Configure listeners:
     - Port 80 → Forward to target group
     - Port 443 → Redirect to 80 (or use SSL certificate)
   - Add EC2 instances to target group

3. **Register Instances**
   ```bash
   aws elbv2 register-targets \
     --target-group-arn arn:aws:elasticloadbalancing:... \
     --targets Id=i-1234567890abcdef0
   ```

### DNS Configuration

```bash
# Get Load Balancer DNS
aws elbv2 describe-load-balancers

# Update Route 53 (if using)
# Point your domain to Load Balancer DNS
```

## Auto-Scaling

### Create Auto-Scaling Group

```bash
# 1. Create Launch Template
aws ec2 create-launch-template \
  --launch-template-name ppmi-api-template \
  --version-description "PPMI API Template" \
  --launch-template-data '{
    "ImageId": "ami-0c55b159cbfafe1f0",
    "InstanceType": "t3.medium",
    "UserData": "IyEvYmluL2Jhc2gKZG9ja2VyIHJ1biAtZCAtLW5hbWUgcHBtaS1hcGkgLXAgODAwMDo4MDAwIHBwbWktYXBpOmxhdGVzdA=="
  }'

# 2. Create Auto-Scaling Group
aws autoscaling create-auto-scaling-group \
  --auto-scaling-group-name ppmi-api-asg \
  --launch-template LaunchTemplateName=ppmi-api-template,Version='$Latest' \
  --min-size 2 \
  --max-size 10 \
  --desired-capacity 3 \
  --target-group-arns arn:aws:elasticloadbalancing:...

# 3. Create Scaling Policies
aws autoscaling put-scaling-policy \
  --auto-scaling-group-name ppmi-api-asg \
  --policy-name scale-up-policy \
  --policy-type TargetTrackingScaling \
  --target-tracking-configuration '{
    "TargetValue": 70.0,
    "PredefinedMetricSpecification": {
      "PredefinedMetricType": "ASGAverageCPUUtilization"
    }
  }'
```

## Monitoring

### CloudWatch Monitoring

1. **Enable Detailed Monitoring**
   ```bash
   aws ec2 monitor-instances --instance-ids i-1234567890abcdef0
   ```

2. **Create Alarms**
   ```bash
   # CPU Usage Alarm
   aws cloudwatch put-metric-alarm \
     --alarm-name ppmi-api-high-cpu \
     --alarm-description "Alert when CPU > 80%" \
     --metric-name CPUUtilization \
     --namespace AWS/EC2 \
     --statistic Average \
     --period 300 \
     --threshold 80 \
     --comparison-operator GreaterThanThreshold \
     --alarm-actions arn:aws:sns:us-east-1:123456789012:my-topic
   ```

3. **Application Logs to CloudWatch**
   ```bash
   # Install CloudWatch agent
   wget https://s3.amazonaws.com/amazoncloudwatch-agent/amazon_linux/amd64/latest/amazon-cloudwatch-agent.rpm
   sudo rpm -U ./amazon-cloudwatch-agent.rpm
   
   # Configure to send logs
   sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
     -a query -m ec2 -c default -s
   ```

### Performance Monitoring

Monitor key metrics:

- **Request Latency**: `GET /api/health` should return < 100ms
- **Model Inference Time**: ~5-50ms per request
- **Memory Usage**: Should stabilize after startup
- **Error Rate**: Should be < 0.1%

## Cost Estimation

### Monthly Costs (Approximate)

| Resource | Instance Type | Quantity | Monthly Cost |
|----------|---------------|----------|------------|
| EC2 | t3.medium | 2 (ASG) | $30-40 |
| Data Transfer | Out to Internet | 100 GB | $10-15 |
| S3 Storage | Models | 10 GB | $0.50 |
| ELB | Application LB | 1 | $15-20 |
| CloudWatch | Monitoring | Standard | $0-5 |
| **Total** | | | **$55-80** |

### Cost Optimization

- Use Reserved Instances (save ~30%)
- Use Savings Plans (save ~20%)
- Set auto-scaling limits to prevent overspending
- Use S3 lifecycle policies for old logs

## Security

### Security Best Practices

1. **Network Security**
   ```
   - Use Security Groups to restrict access
   - Use VPC with private subnets where possible
   - Use VPN/Bastion for EC2 SSH access
   ```

2. **Authentication**
   ```python
   # Add API Key authentication (optional)
   from fastapi import Header, HTTPException
   
   async def verify_api_key(x_api_key: str = Header(None)):
       if x_api_key != os.getenv("API_KEY"):
           raise HTTPException(status_code=403, detail="Invalid API key")
       return x_api_key
   ```

3. **HTTPS/SSL**
   ```bash
   # Using ACM (AWS Certificate Manager)
   # Request free SSL certificate for your domain
   # Configure ALB to use certificate
   # Redirect HTTP to HTTPS
   ```

4. **Data Protection**
   - Enable S3 bucket versioning
   - Enable S3 server-side encryption
   - Use VPC endpoints for S3 access
   - Enable CloudTrail for audit logging

5. **IAM Roles**
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": [
           "s3:GetObject"
         ],
         "Resource": "arn:aws:s3:::ppmi-models-prod/models/*"
       }
     ]
   }
   ```

### Compliance

- Enable VPC Flow Logs
- Enable CloudTrail logging
- Use AWS KMS for encryption
- Implement API rate limiting
- Document data retention policies

## Deployment Checklist

- [ ] AWS Account created
- [ ] EC2 instance launched
- [ ] Security groups configured
- [ ] IAM role created and attached
- [ ] Application deployed (Python with venv)
- [ ] Models uploaded to S3 (if applicable)
- [ ] Load Balancer configured
- [ ] Auto-scaling groups created
- [ ] CloudWatch alarms set up
- [ ] SSL/HTTPS configured
- [ ] DNS records updated
- [ ] Health checks passing
- [ ] Load testing completed
- [ ] Monitoring dashboards created
- [ ] Backup/disaster recovery plan

## Troubleshooting

### Instance Connection Failed
```bash
# Check security group
aws ec2 describe-security-groups --group-ids sg-xxxxxxxx

# Check instance status
aws ec2 describe-instance-status --instance-ids i-xxxxxxxx
```

### Application Not Starting
```bash
# Check systemd service
sudo systemctl status ppmi-api
sudo journalctl -u ppmi-api -f
```

### Models Not Accessible
```bash
# Check S3 bucket access
aws s3 ls s3://ppmi-models-prod/models/

# Check IAM role
aws iam get-role --role-name ec2-ppmi-role

# Verify environment variables
env | grep AWS
```

### Health Check Failing
```bash
# Manual health check
curl http://localhost:8000/api/health

# Check API logs
sudo journalctl -u ppmi-api -f | tail -50
```

## Additional Resources

- [AWS EC2 Documentation](https://docs.aws.amazon.com/ec2/)
- [AWS ALB Documentation](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/)
- [AWS Auto Scaling Documentation](https://docs.aws.amazon.com/autoscaling/)
- [AWS CloudWatch Documentation](https://docs.aws.amazon.com/cloudwatch/)
- [AWS S3 Documentation](https://docs.aws.amazon.com/s3/)

---

**Last Updated**: 2024
