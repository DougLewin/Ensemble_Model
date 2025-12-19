"""
AWS S3 Data Loader Module
==========================
Handles loading NASDAQ data from AWS S3 bucket with proper authentication.

Author: Full-Stack Quantitative Developer
Date: December 18, 2025
"""

import pandas as pd
import boto3
import os
from io import StringIO
from typing import Optional
import warnings
warnings.filterwarnings('ignore')


class S3DataLoader:
    """
    Load market data from AWS S3 bucket.
    
    Supports both credentials-based and role-based authentication.
    """
    
    def __init__(
        self,
        bucket_name: str,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        region_name: str = 'us-east-1'
    ):
        """
        Initialize S3 data loader.
        
        Args:
            bucket_name: Name of the S3 bucket
            aws_access_key_id: AWS access key (or None to use env/IAM role)
            aws_secret_access_key: AWS secret key (or None to use env/IAM role)
            region_name: AWS region name (default: us-east-1)
        """
        self.bucket_name = bucket_name
        self.region_name = region_name
        
        # Initialize S3 client with provided credentials or defaults
        if aws_access_key_id and aws_secret_access_key:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                region_name=region_name
            )
        else:
            # Use default credentials (env vars, IAM role, or AWS config)
            self.s3_client = boto3.client('s3', region_name=region_name)
    
    def load_csv_from_s3(
        self,
        s3_key: str,
        use_cache: bool = True,
        cache_ttl_hours: int = 24
    ) -> pd.DataFrame:
        """
        Load CSV file from S3 bucket with smart local caching.
        
        Args:
            s3_key: S3 object key (path to file in bucket)
            use_cache: Whether to use local cache file if available
            cache_ttl_hours: Cache time-to-live in hours (default: 24)
            
        Returns:
            DataFrame with the loaded data
            
        Raises:
            Exception: If file cannot be loaded from S3
        """
        cache_filename = os.path.basename(s3_key)
        
        # Check if local cache exists and is recent
        if use_cache and os.path.exists(cache_filename):
            cache_age_seconds = os.path.getmtime(cache_filename)
            cache_age_hours = (pd.Timestamp.now().timestamp() - cache_age_seconds) / 3600
            
            if cache_age_hours < cache_ttl_hours:
                print(f"\n{'='*60}")
                print("LOADING FROM LOCAL CACHE")
                print(f"{'='*60}")
                print(f"Cache file: {cache_filename}")
                print(f"Cache age: {cache_age_hours:.1f} hours (TTL: {cache_ttl_hours}h)")
                
                df = pd.read_csv(cache_filename)
                print(f"✅ Loaded {len(df):,} rows from cache")
                return df
            else:
                print(f"\n⚠️ Cache expired ({cache_age_hours:.1f}h > {cache_ttl_hours}h), downloading fresh data...")
        
        try:
            print(f"\n{'='*60}")
            print("S3 DATA LOADING")
            print(f"{'='*60}")
            print(f"Bucket: {self.bucket_name}")
            print(f"Key: {s3_key}")
            print(f"Region: {self.region_name}")
            
            # Download file from S3
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            
            # Read CSV content
            csv_content = response['Body'].read().decode('utf-8')
            df = pd.read_csv(StringIO(csv_content))
            
            print(f"✅ Successfully loaded {len(df):,} rows from S3")
            print(f"Columns: {list(df.columns)}")
            
            # Save to local cache
            if use_cache:
                df.to_csv(cache_filename, index=False)
                print(f"📦 Cached locally as: {cache_filename}")
            
            return df
            
        except Exception as e:
            print(f"❌ Error loading from S3: {str(e)}")
            raise
    
    def load_nasdaq_data(
        self,
        s3_key: str,
        use_cache: bool = True,
        cache_ttl_hours: int = 24
    ) -> pd.DataFrame:
        """
        Load NASDAQ data from S3 and format for trading system.
        
        Args:
            s3_key: S3 object key (path to NASDAQ CSV in bucket)
            use_cache: Whether to use local cache file if available
            cache_ttl_hours: Cache time-to-live in hours (default: 24)
            
        Returns:
            DataFrame with MultiIndex (date, ticker) and OHLCV columns
        """
        # Load raw data from S3 (or cache)
        df = self.load_csv_from_s3(s3_key, use_cache=use_cache, cache_ttl_hours=cache_ttl_hours)
        
        # Standardize column names (lowercase)
        df.columns = df.columns.str.lower()
        
        # Rename columns to match expected format
        # Handle various column name formats: 'code', 'aokcode', etc.
        column_mapping = {
            'code': 'ticker',
            'aokcode': 'ticker',  # Handle 'aokCODE' after lowercase
            'ticker': 'ticker',
            'date': 'date',
            'open': 'open',
            'high': 'high',
            'low': 'low',
            'close': 'close',
            'volume': 'volume'
        }
        df = df.rename(columns=column_mapping)
        
        # Convert date to datetime
        df['date'] = pd.to_datetime(df['date'])
        
        # Keep only required columns
        required_cols = ['date', 'ticker', 'open', 'high', 'low', 'close', 'volume']
        df = df[required_cols]
        
        # Remove rows with missing/NaN ticker values
        df = df.dropna(subset=['ticker'])
        
        # Ensure ticker is string type
        df['ticker'] = df['ticker'].astype(str)
        
        # Set MultiIndex
        df = df.set_index(['date', 'ticker']).sort_index()
        
        # Remove any duplicates
        df = df[~df.index.duplicated(keep='first')]
        
        print(f"\n📊 Data Summary:")
        print(f"   Date Range: {df.index.get_level_values('date').min()} to {df.index.get_level_values('date').max()}")
        print(f"   Unique Tickers: {df.index.get_level_values('ticker').nunique()}")
        print(f"   Total Records: {len(df):,}")
        
        return df
    
    def list_bucket_contents(self, prefix: str = '') -> list:
        """
        List all objects in the S3 bucket with optional prefix.
        
        Args:
            prefix: Optional prefix to filter objects
            
        Returns:
            List of object keys
        """
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            if 'Contents' in response:
                objects = [obj['Key'] for obj in response['Contents']]
                print(f"\nFound {len(objects)} objects in bucket '{self.bucket_name}':")
                for obj in objects:
                    print(f"  - {obj}")
                return objects
            else:
                print(f"\nNo objects found in bucket '{self.bucket_name}' with prefix '{prefix}'")
                return []
                
        except Exception as e:
            print(f"❌ Error listing bucket contents: {str(e)}")
            return []
    
    def test_connection(self) -> bool:
        """
        Test S3 connection and bucket access.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            print(f"\n🔍 Testing S3 connection...")
            print(f"Bucket: {self.bucket_name}")
            
            # Try to list bucket contents (just first few items)
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                MaxKeys=5
            )
            
            print(f"✅ Connection successful!")
            
            if 'Contents' in response:
                print(f"Sample objects found:")
                for obj in response['Contents'][:5]:
                    print(f"  - {obj['Key']}")
            else:
                print("Bucket is empty or no objects found")
            
            return True
            
        except Exception as e:
            print(f"❌ Connection failed: {str(e)}")
            return False


def load_nasdaq_from_s3(
    bucket_name: str,
    s3_key: str,
    aws_access_key_id: Optional[str] = None,
    aws_secret_access_key: Optional[str] = None,
    region_name: str = 'us-east-1',
    use_cache: bool = True
) -> pd.DataFrame:
    """
    Convenience function to load NASDAQ data from S3.
    
    Args:
        bucket_name: Name of the S3 bucket
        s3_key: S3 object key (path to NASDAQ CSV in bucket)
        aws_access_key_id: AWS access key (optional)
        aws_secret_access_key: AWS secret key (optional)
        region_name: AWS region name (default: us-east-1)
        use_cache: Whether to cache the downloaded file locally
        
    Returns:
        DataFrame with MultiIndex (date, ticker) and OHLCV columns
    """
    loader = S3DataLoader(
        bucket_name=bucket_name,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=region_name
    )
    
    return loader.load_nasdaq_data(s3_key, use_cache=use_cache)


if __name__ == "__main__":
    """
    Test script for S3 data loader.
    Set environment variables before running:
    - AWS_S3_BUCKET_NAME
    - AWS_S3_KEY
    - AWS_ACCESS_KEY_ID (optional if using IAM role)
    - AWS_SECRET_ACCESS_KEY (optional if using IAM role)
    - AWS_REGION (optional, defaults to us-east-1)
    """
    
    # Load from environment variables
    bucket_name = os.getenv('AWS_S3_BUCKET_NAME', 'my-nasdaq-data-bucket')
    s3_key = os.getenv('AWS_S3_KEY', 'NASDAQ.csv')
    aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    region_name = os.getenv('AWS_REGION', 'us-east-1')
    
    print("S3 Data Loader Test")
    print("=" * 60)
    
    # Create loader
    loader = S3DataLoader(
        bucket_name=bucket_name,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=region_name
    )
    
    # Test connection
    if loader.test_connection():
        # List bucket contents
        loader.list_bucket_contents()
        
        # Try to load data
        try:
            df = loader.load_nasdaq_data(s3_key)
            print("\n✅ Data loaded successfully!")
            print(f"\nFirst few rows:")
            print(df.head())
        except Exception as e:
            print(f"\n❌ Failed to load data: {str(e)}")
