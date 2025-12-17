"""
AWS S3 Setup Helper Script
===========================
Interactive script to help configure AWS S3 integration.

Run this script to:
- Create .env file from template
- Test AWS credentials
- Verify S3 bucket access
- Upload data to S3 (optional)

Author: Full-Stack Quantitative Developer
Date: December 18, 2025
"""

import os
import sys
from pathlib import Path


def create_env_file():
    """Create .env file from .env.example if it doesn't exist."""
    env_file = Path('.env')
    env_example = Path('.env.example')
    
    if env_file.exists():
        print("✅ .env file already exists")
        response = input("Do you want to overwrite it? (y/n): ")
        if response.lower() != 'y':
            print("Keeping existing .env file")
            return False
    
    if not env_example.exists():
        print("❌ .env.example not found")
        return False
    
    # Copy template
    env_file.write_text(env_example.read_text())
    print("✅ Created .env file from template")
    print("📝 Please edit .env file with your AWS credentials")
    return True


def test_aws_credentials():
    """Test if AWS credentials are configured."""
    print("\n" + "="*60)
    print("Testing AWS Credentials")
    print("="*60)
    
    try:
        import boto3
        from dotenv import load_dotenv
        
        # Load environment variables
        load_dotenv()
        
        # Get credentials from environment
        bucket_name = os.getenv('AWS_S3_BUCKET_NAME')
        region = os.getenv('AWS_REGION', 'us-east-1')
        
        if not bucket_name:
            print("❌ AWS_S3_BUCKET_NAME not set in .env file")
            return False
        
        print(f"Bucket: {bucket_name}")
        print(f"Region: {region}")
        
        # Create S3 client
        s3_client = boto3.client('s3', region_name=region)
        
        # Test connection by listing bucket
        response = s3_client.list_objects_v2(
            Bucket=bucket_name,
            MaxKeys=5
        )
        
        print("✅ Successfully connected to S3!")
        
        if 'Contents' in response:
            print(f"\nFound {len(response['Contents'])} objects (showing up to 5):")
            for obj in response['Contents']:
                print(f"  - {obj['Key']}")
        else:
            print("\nBucket is empty")
        
        return True
        
    except ImportError:
        print("❌ boto3 not installed. Run: pip install boto3 python-dotenv")
        return False
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("\nPossible issues:")
        print("  - Check AWS credentials in .env file")
        print("  - Verify bucket name is correct")
        print("  - Ensure IAM permissions include s3:ListBucket")
        return False


def test_data_loading():
    """Test loading data from S3."""
    print("\n" + "="*60)
    print("Testing Data Loading")
    print("="*60)
    
    try:
        from s3_data_loader import S3DataLoader
        from config import AWSConfig
        from dotenv import load_dotenv
        
        # Load environment
        load_dotenv()
        
        # Get config
        aws_config = AWSConfig()
        
        print(f"Bucket: {aws_config.bucket_name}")
        print(f"Key: {aws_config.s3_key}")
        
        # Create loader
        loader = S3DataLoader(
            bucket_name=aws_config.bucket_name,
            aws_access_key_id=aws_config.aws_access_key_id,
            aws_secret_access_key=aws_config.aws_secret_access_key,
            region_name=aws_config.region_name
        )
        
        # Try to load data
        df = loader.load_nasdaq_data(aws_config.s3_key, use_cache=True)
        
        print("\n✅ Data loaded successfully!")
        print(f"Rows: {len(df):,}")
        print(f"Tickers: {df.index.get_level_values('ticker').nunique()}")
        print(f"Date Range: {df.index.get_level_values('date').min()} to {df.index.get_level_values('date').max()}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {str(e)}")
        print("Make sure all dependencies are installed: pip install -r requirements.txt")
        return False
    
    except Exception as e:
        print(f"❌ Error loading data: {str(e)}")
        return False


def upload_to_s3():
    """Interactive upload of local CSV to S3."""
    print("\n" + "="*60)
    print("Upload Data to S3")
    print("="*60)
    
    try:
        import boto3
        from dotenv import load_dotenv
        
        load_dotenv()
        
        # Get config
        bucket_name = os.getenv('AWS_S3_BUCKET_NAME')
        region = os.getenv('AWS_REGION', 'us-east-1')
        
        # Ask for local file
        local_file = input("Enter path to local CSV file (or press Enter to skip): ").strip()
        
        if not local_file:
            print("Skipping upload")
            return False
        
        if not os.path.exists(local_file):
            print(f"❌ File not found: {local_file}")
            return False
        
        # Ask for S3 key
        default_key = os.path.basename(local_file)
        s3_key = input(f"Enter S3 key (default: {default_key}): ").strip() or default_key
        
        # Confirm
        print(f"\nReady to upload:")
        print(f"  Local: {local_file}")
        print(f"  S3: s3://{bucket_name}/{s3_key}")
        
        confirm = input("Proceed? (y/n): ")
        if confirm.lower() != 'y':
            print("Upload cancelled")
            return False
        
        # Upload
        s3_client = boto3.client('s3', region_name=region)
        
        print("Uploading...")
        s3_client.upload_file(local_file, bucket_name, s3_key)
        
        print("✅ Upload successful!")
        print(f"Data is now available at: s3://{bucket_name}/{s3_key}")
        
        # Update .env with new key if different
        if s3_key != os.getenv('AWS_S3_KEY'):
            print(f"\n💡 Tip: Update AWS_S3_KEY in .env to: {s3_key}")
        
        return True
        
    except Exception as e:
        print(f"❌ Upload failed: {str(e)}")
        return False


def main():
    """Main setup wizard."""
    print("="*60)
    print("AWS S3 Setup Helper for Ensemble Trading System")
    print("="*60)
    
    # Step 1: Create .env file
    print("\n📝 Step 1: Environment Configuration")
    create_env_file()
    
    input("\n⏸️  Press Enter after you've edited .env with your credentials...")
    
    # Step 2: Test credentials
    print("\n🔍 Step 2: Testing AWS Connection")
    if not test_aws_credentials():
        print("\n❌ Setup incomplete. Please fix the issues above and try again.")
        return
    
    # Step 3: Optional upload
    print("\n📤 Step 3: Upload Data (Optional)")
    response = input("Do you want to upload a local CSV to S3? (y/n): ")
    if response.lower() == 'y':
        upload_to_s3()
    
    # Step 4: Test data loading
    print("\n📊 Step 4: Testing Data Loading")
    if test_data_loading():
        print("\n" + "="*60)
        print("✅ Setup Complete!")
        print("="*60)
        print("\nYou can now run:")
        print("  - streamlit run app.py     (Dashboard)")
        print("  - python main.py           (CLI Script)")
        print("\nBoth will automatically load data from S3!")
    else:
        print("\n⚠️  Setup partially complete")
        print("S3 connection works, but couldn't load data.")
        print("Make sure your CSV file is uploaded to S3.")


if __name__ == "__main__":
    main()
