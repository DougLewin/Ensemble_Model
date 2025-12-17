# Streamlit Cloud Deployment Guide
## AWS S3 Integration

---

## 📋 Overview

This guide explains how to deploy your Ensemble Trading System to Streamlit Cloud with AWS S3 integration.

---

## 🚀 Quick Deployment Steps

### 1. Push to GitHub

Ensure your code is pushed to GitHub:

```powershell
git add .
git commit -m "Add AWS S3 integration"
git push origin main
```

### 2. Deploy to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io/)
2. Click "New app"
3. Select your GitHub repository: `DougLewin/Ensemble_Model`
4. Set main file path: `app.py`
5. Click "Deploy"

### 3. Configure Secrets

1. In your deployed app, click the **three dots menu** (⋮) → **Settings**
2. Go to the **"Secrets"** tab
3. Copy the content from `.streamlit/secrets.toml.example`
4. **Replace placeholder values** with your real AWS credentials:

```toml
# Streamlit Cloud Secrets Configuration
[aws]
AWS_S3_BUCKET_NAME = "your-bucket-name-here"
AWS_S3_KEY = "NASDAQ.csv"
AWS_REGION = "us-east-1"
AWS_ACCESS_KEY_ID = "AKIA..."
AWS_SECRET_ACCESS_KEY = "your-secret-access-key-here"

[data]
USE_S3 = "true"
LOCAL_FALLBACK = "NASDAQ.csv"
```

5. Click **"Save"**
6. Your app will automatically restart with the secrets

---

## 🔐 Security Notes

### ✅ Safe:
- Secrets in Streamlit Cloud are encrypted
- Never committed to GitHub
- Only accessible to your app
- Can be updated anytime in Settings

### ⚠️ Important:
- Never commit `.streamlit/secrets.toml` to git (it's in `.gitignore`)
- Use IAM roles with minimal permissions
- Rotate credentials regularly
- Only grant `s3:GetObject` and `s3:ListBucket` permissions

---

## 🔄 How It Works

The system automatically detects the environment:

### Local Development:
```
.env file → Environment variables → App loads from S3
```

### Streamlit Cloud:
```
Secrets → st.secrets → App loads from S3
```

The `config.py` file handles both automatically:
1. First checks for Streamlit secrets
2. Falls back to environment variables
3. Uses defaults if neither found

---

## 📊 Data Source Priority

The app follows this priority order:

1. **Streamlit Secrets** (if `USE_S3=true` in secrets)
   - Loads from S3 bucket specified in secrets
   
2. **Environment Variables** (if `.env` file exists locally)
   - Loads from S3 bucket specified in `.env`
   
3. **Local Fallback** (if S3 fails)
   - Loads from `LOCAL_FALLBACK` file

---

## 🧪 Testing Deployment

### Test Locally First:
```powershell
streamlit run app.py
```

Check that S3 loading works before deploying.

### After Deployment:
1. Visit your Streamlit Cloud URL
2. Check for success message: "✅ Data loaded from S3"
3. Verify data displays correctly
4. Check logs for any errors

---

## 🐛 Troubleshooting

### App fails to start
**Issue**: Missing dependencies

**Solution**: Ensure `requirements.txt` includes:
```
boto3>=1.28.0
python-dotenv>=1.0.0
```

### "NoCredentialsError"
**Issue**: Secrets not configured

**Solution**: 
1. Go to app Settings → Secrets
2. Verify all AWS credentials are set
3. Check for typos in secret keys

### "Access Denied" errors
**Issue**: Insufficient S3 permissions

**Solution**:
1. Verify IAM policy includes:
   ```json
   {
     "Effect": "Allow",
     "Action": ["s3:GetObject", "s3:ListBucket"],
     "Resource": [
       "arn:aws:s3:::your-bucket-name",
       "arn:aws:s3:::your-bucket-name/*"
     ]
   }
   ```

### Data not loading
**Issue**: Wrong bucket/key in secrets

**Solution**:
1. Check bucket name matches exactly
2. Verify S3 key (file path) is correct
3. Ensure file exists in S3 bucket

### App uses local file instead of S3
**Issue**: `USE_S3` not set to "true"

**Solution**:
1. Go to Secrets settings
2. Ensure: `USE_S3 = "true"` (not `false`)
3. Save and restart app

---

## 📝 Secrets Template

Copy this exact format to Streamlit Cloud Secrets:

```toml
[aws]
AWS_S3_BUCKET_NAME = "your-bucket-name"
AWS_S3_KEY = "NASDAQ.csv"
AWS_REGION = "us-east-1"
AWS_ACCESS_KEY_ID = "AKIA..."
AWS_SECRET_ACCESS_KEY = "your-secret-key"

[data]
USE_S3 = "true"
LOCAL_FALLBACK = "NASDAQ.csv"
```

**Important**: 
- Use double quotes for values
- Don't add extra spaces
- Use exact key names (case-sensitive)

---

## 🔄 Updating Secrets

To update AWS credentials or configuration:

1. Go to your app on Streamlit Cloud
2. Click **three dots menu** → **Settings**
3. Go to **"Secrets"** tab
4. Edit the values
5. Click **"Save"**
6. App automatically restarts

No need to redeploy!

---

## 🌐 Environment-Specific Settings

### Local Development (.env):
```bash
USE_S3=true
AWS_S3_BUCKET_NAME=nasdaq-history
AWS_S3_KEY=NASDAQ.csv
```

### Streamlit Cloud (secrets):
```toml
[data]
USE_S3 = "true"

[aws]
AWS_S3_BUCKET_NAME = "nasdaq-history"
AWS_S3_KEY = "NASDAQ.csv"
```

Both work identically, just different formats!

---

## ✅ Deployment Checklist

Before deploying:
- [ ] Code pushed to GitHub
- [ ] `.env` file in `.gitignore` (yes, it is!)
- [ ] `requirements.txt` includes boto3 and python-dotenv
- [ ] Tested locally with S3 connection
- [ ] AWS credentials ready
- [ ] S3 bucket contains data file

After deploying:
- [ ] App deploys successfully
- [ ] Secrets configured in Streamlit Cloud
- [ ] App loads data from S3
- [ ] Dashboard displays correctly
- [ ] No errors in logs

---

## 💡 Pro Tips

1. **Test locally first** - Much faster to debug
2. **Check logs** - Streamlit Cloud shows detailed error messages
3. **Use IAM roles** - More secure than access keys for production
4. **Monitor costs** - S3 GET requests incur small charges
5. **Cache data** - Streamlit caching reduces API calls
6. **Version your data** - Keep old versions in S3 for rollback

---

## 📞 Support

If you encounter issues:

1. Check Streamlit Cloud logs (click "Manage app" → "Logs")
2. Verify secrets are set correctly
3. Test S3 connection locally with: `python setup_s3.py`
4. Review AWS CloudTrail for access denied errors
5. Check this guide's troubleshooting section

---

**Last Updated**: December 18, 2025
