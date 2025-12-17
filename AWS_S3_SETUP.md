# AWS S3 Integration Guide
## Ensemble Trading System

This guide explains how to configure the system to load NASDAQ data from AWS S3.

---

## 📋 Overview

The system now supports loading market data from AWS S3 buckets, with automatic fallback to local files if needed. This enables:
- Centralized data storage
- Easy data updates without redeploying code
- Shared data access across multiple environments
- Automatic caching for performance

---

## 🔧 Setup Instructions

### 1. Install Dependencies

First, install the required AWS packages:

```powershell
pip install boto3 python-dotenv
```

Or use the updated requirements file:

```powershell
pip install -r requirements.txt
```

### 2. Configure AWS Credentials

#### Option A: Using Environment Variables (Recommended)

1. Copy the example environment file:
   ```powershell
   Copy-Item .env.example .env
   ```

2. Edit `.env` file with your AWS credentials:
   ```
   AWS_S3_BUCKET_NAME=your-bucket-name
   AWS_S3_KEY=NASDAQ.csv
   AWS_REGION=us-east-1
   AWS_ACCESS_KEY_ID=your-access-key-id
   AWS_SECRET_ACCESS_KEY=your-secret-access-key
   ```

3. The `.env` file is automatically ignored by git (never commit credentials!)

#### Option B: Using IAM Roles (For EC2/Lambda)

If running on AWS infrastructure, you can use IAM roles instead of credentials:

1. Set up an IAM role with S3 read permissions
2. In `.env`, leave credentials blank:
   ```
   AWS_S3_BUCKET_NAME=your-bucket-name
   AWS_S3_KEY=NASDAQ.csv
   AWS_REGION=us-east-1
   ```

The AWS SDK will automatically use the IAM role.

### 3. Upload Data to S3

Upload your NASDAQ CSV file to your S3 bucket:

```powershell
aws s3 cp NASDAQ.csv s3://your-bucket-name/NASDAQ.csv
```

Or use the AWS Console:
1. Go to S3 in AWS Console
2. Select your bucket
3. Click "Upload"
4. Choose your NASDAQ.csv file

### 4. Configure Data Source

Edit `config.py` or set environment variables to control data source:

```python
# In .env file
USE_S3=true  # Set to false to use local files
```

---

## 🚀 Usage

### Running the Streamlit Dashboard

The dashboard automatically detects S3 configuration:

```powershell
streamlit run app.py
```

The system will:
1. Check if S3 is enabled in config
2. Load data from S3 if configured
3. Cache the data locally for performance
4. Fall back to local files if S3 fails

### Running the Command-Line Script

```powershell
python main.py
```

Same auto-detection and fallback logic applies.

### Testing S3 Connection

Test your S3 configuration directly:

```powershell
python s3_data_loader.py
```

This will:
- Test connection to your S3 bucket
- List available files
- Attempt to load the NASDAQ data
- Show detailed error messages if something fails

---

## 📊 Data Format

Your NASDAQ CSV file should have these columns:
- `CODE` or `ticker`: Stock ticker symbol
- `DATE` or `date`: Date in YYYY-MM-DD format
- `OPEN`, `HIGH`, `LOW`, `CLOSE`: Price data
- `VOLUME`: Trading volume

The system automatically handles column name variations.

---

## 🔄 Fallback Behavior

The system includes robust fallback logic:

1. **S3 Enabled**: Try to load from S3
   - If successful: Use S3 data (cached locally)
   - If fails: Try local fallback file

2. **S3 Disabled**: Load from local file

3. **Local Fallback**: Specified in config (default: `NASDAQ.csv`)

---

## ⚙️ Configuration Options

### Environment Variables (.env)

```bash
# Required for S3
AWS_S3_BUCKET_NAME=my-nasdaq-data
AWS_S3_KEY=NASDAQ.csv
AWS_REGION=us-east-1

# Optional: Leave blank to use IAM role
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=abc123...

# Data source control
USE_S3=true
LOCAL_FALLBACK=NASDAQ.csv
```

### Python Configuration (config.py)

```python
from config import AWSConfig

aws_config = AWSConfig()
aws_config.use_s3 = True
aws_config.bucket_name = "my-bucket"
aws_config.s3_key = "data/NASDAQ.csv"
aws_config.use_cache = True  # Cache downloaded files
```

---

## 🔐 Security Best Practices

1. **Never commit credentials**
   - `.env` is in `.gitignore`
   - Use environment variables or IAM roles

2. **Use IAM roles when possible**
   - Recommended for production
   - No credentials to manage

3. **Limit S3 permissions**
   - Grant only `s3:GetObject` permission
   - Restrict to specific bucket/prefix

4. **Rotate credentials regularly**
   - Use AWS IAM to manage access keys
   - Set expiration policies

### Example IAM Policy

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::your-bucket-name",
        "arn:aws:s3:::your-bucket-name/*"
      ]
    }
  ]
}
```

---

## 🐛 Troubleshooting

### Error: "NoCredentialsError"

**Problem**: AWS credentials not found

**Solutions**:
1. Check `.env` file exists and has correct credentials
2. Verify environment variables are loaded
3. Check IAM role if using EC2/Lambda

### Error: "Access Denied"

**Problem**: Insufficient S3 permissions

**Solutions**:
1. Check IAM policy includes `s3:GetObject`
2. Verify bucket name is correct
3. Check bucket permissions/policies

### Error: "NoSuchBucket"

**Problem**: Bucket doesn't exist or wrong region

**Solutions**:
1. Verify bucket name in `.env`
2. Check AWS region setting
3. Confirm bucket exists in AWS Console

### Data Loads but Looks Wrong

**Problem**: Column names don't match

**Solutions**:
1. Check CSV format matches expected structure
2. Verify column names (CODE/ticker, DATE/date, etc.)
3. Review `s3_data_loader.py` column mapping

---

## 📁 File Structure

```
Ensemble_Model/
├── s3_data_loader.py      # S3 integration module
├── config.py              # Configuration (includes AWSConfig)
├── app.py                 # Streamlit dashboard (S3-enabled)
├── main.py                # CLI script (S3-enabled)
├── .env.example           # Template for credentials
├── .env                   # Your actual credentials (git-ignored)
├── AWS_S3_SETUP.md       # This guide
└── requirements.txt       # Dependencies (includes boto3)
```

---

## 🔄 Migration from Local Files

To migrate from local CSV to S3:

1. Keep your local CSV as fallback
2. Upload CSV to S3 bucket
3. Configure `.env` with S3 settings
4. Set `USE_S3=true`
5. Test with `python s3_data_loader.py`
6. Run dashboard/scripts as normal

The system will automatically use S3 and cache locally!

---

## 💡 Tips

1. **Use caching**: Set `use_cache=True` (default) for better performance
2. **Test connection first**: Run `s3_data_loader.py` standalone
3. **Keep local fallback**: Always have a backup CSV file
4. **Monitor costs**: S3 GET requests incur small charges
5. **Update data**: Just upload new CSV to S3, no code changes needed

---

## 📞 Support

For issues:
1. Check error messages in console/logs
2. Verify AWS credentials and permissions
3. Test S3 connection with standalone script
4. Review this guide's troubleshooting section

---

## 🎯 Quick Start Checklist

- [ ] Install boto3 and python-dotenv
- [ ] Copy `.env.example` to `.env`
- [ ] Fill in AWS credentials in `.env`
- [ ] Upload NASDAQ.csv to S3 bucket
- [ ] Test connection: `python s3_data_loader.py`
- [ ] Run dashboard: `streamlit run app.py`
- [ ] Verify data loads from S3

---

**Last Updated**: December 18, 2025
