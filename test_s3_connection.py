"""
S3 Connection Debugging Script
===============================
Tests AWS S3 connection step-by-step to identify issues.
"""

import os
import boto3
from dotenv import load_dotenv
from botocore.exceptions import ClientError, NoCredentialsError

# Load environment variables
load_dotenv()

print("=" * 70)
print("S3 CONNECTION DEBUG TEST")
print("=" * 70)

# Step 1: Check environment variables
print("\n[STEP 1] Checking Environment Variables")
print("-" * 70)

bucket_name = os.getenv('AWS_S3_BUCKET_NAME')
s3_key = os.getenv('AWS_S3_KEY')
access_key = os.getenv('AWS_ACCESS_KEY_ID')
secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
region = os.getenv('AWS_REGION', 'us-east-1')
use_s3 = os.getenv('USE_S3', 'false')

print(f"AWS_S3_BUCKET_NAME: {bucket_name}")
print(f"AWS_S3_KEY: {s3_key}")
print(f"AWS_REGION: {region}")
print(f"USE_S3: {use_s3}")
print(f"AWS_ACCESS_KEY_ID: {'*' * 10 + access_key[-4:] if access_key and len(access_key) > 4 else 'NOT SET'}")
print(f"AWS_SECRET_ACCESS_KEY: {'*' * 10 + '****' if secret_key else 'NOT SET'}")

if not access_key or access_key == 'your-access-key-here':
    print("\n❌ ERROR: AWS_ACCESS_KEY_ID not configured properly!")
    print("   Please edit .env file and add your real AWS credentials.")
    exit(1)

if not secret_key or secret_key == 'your-secret-key-here':
    print("\n❌ ERROR: AWS_SECRET_ACCESS_KEY not configured properly!")
    print("   Please edit .env file and add your real AWS credentials.")
    exit(1)

if not bucket_name or bucket_name == 'your-bucket-name-here':
    print("\n❌ ERROR: AWS_S3_BUCKET_NAME not configured properly!")
    print("   Please edit .env file and add your real S3 bucket name.")
    exit(1)

print("\n✅ Environment variables loaded successfully")

# Step 2: Create S3 client
print("\n[STEP 2] Creating S3 Client")
print("-" * 70)

try:
    s3_client = boto3.client(
        's3',
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region
    )
    print("✅ S3 client created successfully")
except Exception as e:
    print(f"❌ Failed to create S3 client: {str(e)}")
    exit(1)

# Step 3: Test credentials by listing buckets
print("\n[STEP 3] Testing Credentials (List Buckets)")
print("-" * 70)

try:
    response = s3_client.list_buckets()
    print(f"✅ Credentials are VALID!")
    print(f"\nYou have access to {len(response['Buckets'])} bucket(s):")
    for bucket in response['Buckets']:
        print(f"   - {bucket['Name']}")
        if bucket['Name'] == bucket_name:
            print(f"     ✅ Target bucket '{bucket_name}' found!")
except NoCredentialsError:
    print("❌ No credentials found!")
    print("   Check your .env file has AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY")
    exit(1)
except ClientError as e:
    error_code = e.response['Error']['Code']
    error_msg = e.response['Error']['Message']
    print(f"❌ AWS Error: {error_code}")
    print(f"   Message: {error_msg}")
    
    if error_code == 'InvalidAccessKeyId':
        print("\n   SOLUTION: Your AWS Access Key ID is invalid.")
        print("   1. Go to AWS IAM Console: https://console.aws.amazon.com/iam/")
        print("   2. Check if the user still exists")
        print("   3. Create new access keys if needed")
        print("   4. Update .env file with new credentials")
    elif error_code == 'SignatureDoesNotMatch':
        print("\n   SOLUTION: Your AWS Secret Access Key is incorrect.")
        print("   1. Verify you copied the full secret key")
        print("   2. Check for extra spaces or newlines")
        print("   3. Create new access keys if needed")
    
    exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {str(e)}")
    exit(1)

# Step 4: Check if target bucket exists
print(f"\n[STEP 4] Checking Target Bucket: {bucket_name}")
print("-" * 70)

try:
    s3_client.head_bucket(Bucket=bucket_name)
    print(f"✅ Bucket '{bucket_name}' exists and is accessible!")
except ClientError as e:
    error_code = e.response['Error']['Code']
    
    if error_code == '404':
        print(f"❌ Bucket '{bucket_name}' does NOT exist!")
        print("\n   Available buckets:")
        for bucket in response['Buckets']:
            print(f"   - {bucket['Name']}")
        print("\n   SOLUTION: Update AWS_S3_BUCKET_NAME in .env to match one of the above")
    elif error_code == '403':
        print(f"❌ Bucket '{bucket_name}' exists but you don't have access!")
        print("   SOLUTION: Grant S3 permissions to your IAM user")
    else:
        print(f"❌ Error: {error_code} - {e.response['Error']['Message']}")
    exit(1)

# Step 5: List objects in bucket
print(f"\n[STEP 5] Listing Objects in Bucket")
print("-" * 70)

try:
    response = s3_client.list_objects_v2(Bucket=bucket_name, MaxKeys=20)
    
    if 'Contents' in response:
        print(f"✅ Found {len(response['Contents'])} object(s) in bucket:")
        for obj in response['Contents']:
            size_mb = obj['Size'] / (1024 * 1024)
            print(f"   - {obj['Key']} ({size_mb:.2f} MB)")
            if obj['Key'] == s3_key:
                print(f"     ✅ Target file '{s3_key}' found!")
    else:
        print(f"⚠️  Bucket '{bucket_name}' is empty!")
        print("   You need to upload data files to this bucket")
        exit(1)
        
except ClientError as e:
    print(f"❌ Error listing objects: {e.response['Error']['Message']}")
    exit(1)

# Step 6: Check if target file exists
print(f"\n[STEP 6] Checking Target File: {s3_key}")
print("-" * 70)

try:
    response = s3_client.head_object(Bucket=bucket_name, Key=s3_key)
    size_mb = response['ContentLength'] / (1024 * 1024)
    print(f"✅ File '{s3_key}' exists!")
    print(f"   Size: {size_mb:.2f} MB")
    print(f"   Last Modified: {response['LastModified']}")
    print(f"   Content Type: {response.get('ContentType', 'N/A')}")
except ClientError as e:
    error_code = e.response['Error']['Code']
    
    if error_code == '404':
        print(f"❌ File '{s3_key}' NOT FOUND in bucket!")
        print("\n   Available files:")
        if 'Contents' in response:
            for obj in response['Contents']:
                print(f"   - {obj['Key']}")
        print("\n   SOLUTION: Update AWS_S3_KEY in .env to match an existing file")
    else:
        print(f"❌ Error: {error_code} - {e.response['Error']['Message']}")
    exit(1)

# Step 7: Try to download and read first few bytes
print(f"\n[STEP 7] Testing File Download")
print("-" * 70)

try:
    response = s3_client.get_object(Bucket=bucket_name, Key=s3_key)
    
    # Read first 500 bytes to check format
    first_bytes = response['Body'].read(500).decode('utf-8')
    
    print("✅ File downloaded successfully!")
    print("\nFirst 500 characters of file:")
    print("-" * 70)
    print(first_bytes)
    print("-" * 70)
    
    # Check if it looks like CSV
    lines = first_bytes.split('\n')
    if len(lines) > 0:
        print(f"\nFirst line (header): {lines[0]}")
        if len(lines) > 1:
            print(f"Second line (data):  {lines[1]}")
            
except Exception as e:
    print(f"❌ Error downloading file: {str(e)}")
    exit(1)

# Final Summary
print("\n" + "=" * 70)
print("✅ ALL TESTS PASSED!")
print("=" * 70)
print("\nYour S3 connection is working correctly!")
print(f"✅ Credentials: Valid")
print(f"✅ Bucket: {bucket_name} (accessible)")
print(f"✅ File: {s3_key} (readable)")
print("\nYou can now set USE_S3=true in your .env file")
print("=" * 70)
