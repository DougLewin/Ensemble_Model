# AWS Credentials Setup Guide

## Overview
This guide explains how to securely manage AWS credentials for local development and production deployment.

## Security Best Practices

### ✅ What IS Safe
- Storing credentials in `.env` file (git-ignored)
- Using environment variables in your local VS Code
- Using Streamlit secrets for cloud deployment
- Committing `.env.example` with placeholder values

### ❌ What is NOT Safe
- Committing `.env` with real credentials to GitHub
- Hardcoding credentials in Python files
- Sharing credentials in chat/email
- Using the same credentials for dev and production

---

## Local Development Setup

### Step 1: Copy Environment Template
```bash
# Copy the template to create your local .env file
cp .env.example .env
```

### Step 2: Get Your AWS Credentials

#### Option A: Create New IAM User (Recommended)
1. Go to [AWS IAM Console](https://console.aws.amazon.com/iam/)
2. Click "Users" → "Add users"
3. Username: `ensemble-trading-dev`
4. Access type: ✅ Programmatic access
5. Permissions: Attach policy `AmazonS3ReadOnlyAccess` (or create custom policy)
6. **Save the credentials** shown on the final screen

#### Option B: Use Existing Credentials
If you already have AWS credentials, locate them in:
- `~/.aws/credentials` (Linux/Mac)
- `C:\Users\YourName\.aws\credentials` (Windows)

### Step 3: Update Your .env File
Edit `.env` and replace the placeholder values:

```bash
# S3 Bucket Configuration
AWS_S3_BUCKET_NAME=your-actual-bucket-name
AWS_S3_KEY=NASDAQ.csv
AWS_REGION=us-east-1

# AWS Credentials (from Step 2)
AWS_ACCESS_KEY_ID=AKIA...YOUR_ACTUAL_KEY
AWS_SECRET_ACCESS_KEY=wJalr...YOUR_ACTUAL_SECRET

# Enable S3 loading
USE_S3=true
```

### Step 4: Verify Setup
```bash
# Test the S3 connection
python s3_data_loader.py
```

---

## Working with Local Files During Development

If you want to develop without S3 (recommended during initial setup):

1. Make sure you have `NASDAQ.csv` in your project directory
2. Set `USE_S3=false` in your `.env` file:

```bash
USE_S3=false
LOCAL_FALLBACK=NASDAQ.csv
```

The system will automatically use local files and won't need AWS credentials.

---

## Production Deployment (Streamlit Cloud)

### Option 1: Streamlit Secrets (Recommended)

1. Go to your Streamlit Cloud app settings
2. Navigate to "Secrets" section
3. Add your credentials in TOML format:

```toml
[aws]
AWS_S3_BUCKET_NAME = "your-bucket-name"
AWS_S3_KEY = "NASDAQ.csv"
AWS_REGION = "us-east-1"
AWS_ACCESS_KEY_ID = "AKIA...YOUR_KEY"
AWS_SECRET_ACCESS_KEY = "wJalr...YOUR_SECRET"

[data]
USE_S3 = "true"
LOCAL_FALLBACK = "NASDAQ.csv"
```

### Option 2: Environment Variables

1. In Streamlit Cloud app settings
2. Navigate to "Advanced settings" → "Environment variables"
3. Add each variable:
   - `AWS_S3_BUCKET_NAME`
   - `AWS_S3_KEY`
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `AWS_REGION`
   - `USE_S3`

---

## Troubleshooting

### Error: "InvalidAccessKeyId"
**Cause:** AWS credentials are incorrect or expired

**Solution:**
1. Verify credentials in AWS IAM Console
2. Make sure you copied the full key without spaces
3. Check if the IAM user still exists and has permissions
4. Try creating new credentials

### Error: "NoCredentialsError"
**Cause:** Credentials not found

**Solution:**
1. Verify `.env` file exists in project root
2. Check environment variables are loaded: `python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('AWS_ACCESS_KEY_ID'))"`
3. Restart your application

### Error: "Access Denied"
**Cause:** IAM user doesn't have S3 permissions

**Solution:**
1. Go to IAM Console → Users → Your User
2. Add permission: `AmazonS3ReadOnlyAccess`
3. Or create custom policy for specific bucket

### S3 Load Fails - Local Fallback Works
**Cause:** S3 configuration issue

**Temporary Solution:**
Set `USE_S3=false` in `.env` to work with local files while debugging

---

## Git Safety Checklist

Before committing code:

- [ ] `.env` is in `.gitignore`
- [ ] No credentials in Python files
- [ ] Only `.env.example` has placeholder values
- [ ] Run: `git status` and verify `.env` is not staged
- [ ] Test: `git diff --staged` to check staged files

### Emergency: Credentials Accidentally Committed

If you accidentally commit credentials:

1. **Immediately** deactivate the credentials in AWS IAM Console
2. Remove from git history:
   ```bash
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch .env" \
     --prune-empty --tag-name-filter cat -- --all
   ```
3. Force push: `git push origin --force --all`
4. Create new credentials

---

## Configuration File Priority

The system loads configuration in this order (first found wins):

1. **Streamlit Secrets** (cloud deployment)
   - Location: `.streamlit/secrets.toml`
   - Automatically loaded on Streamlit Cloud

2. **Environment Variables** (local development)
   - Location: `.env` file
   - Loaded via `python-dotenv`

3. **Default Values** (fallback)
   - Defined in `config.py`

---

## Example Workflow

### Local Development
```bash
# 1. Clone repository
git clone <your-repo>
cd Ensemble_Model

# 2. Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup credentials
cp .env.example .env
# Edit .env with your credentials

# 5. Test S3 connection
python s3_data_loader.py

# 6. Run application
streamlit run app.py
```

### Deploying to Production
```bash
# 1. Push code to GitHub (credentials NOT included)
git add .
git commit -m "Update trading strategies"
git push origin main

# 2. Configure Streamlit Cloud
# - Link GitHub repository
# - Add secrets in Streamlit dashboard
# - Deploy

# 3. Verify deployment
# - Check app logs
# - Test data loading
```

---

## Best Practices

1. **Separate Credentials**
   - Use different credentials for dev and production
   - Limit production credentials to minimum required permissions

2. **Rotate Regularly**
   - Change credentials every 90 days
   - Immediately rotate if compromised

3. **Monitor Usage**
   - Check AWS CloudTrail for suspicious activity
   - Set up billing alerts

4. **Document Access**
   - Keep track of who has access
   - Remove credentials for team members who leave

---

## Support

For additional help:
- AWS IAM Documentation: https://docs.aws.amazon.com/iam/
- Streamlit Secrets: https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management
- boto3 Configuration: https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html
