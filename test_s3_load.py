"""
Quick test to verify S3 data loading with column mapping
"""
from s3_data_loader import S3DataLoader
from config import AWSConfig
import warnings
warnings.filterwarnings('ignore')

print("Testing S3 Data Loader with Column Mapping")
print("=" * 60)

# Load config
aws_config = AWSConfig()

print(f"\nConfiguration:")
print(f"  Bucket: {aws_config.bucket_name}")
print(f"  Key: {aws_config.s3_key}")
print(f"  Region: {aws_config.region_name}")
print(f"  Use S3: {aws_config.use_s3}")

# Create loader
loader = S3DataLoader(
    bucket_name=aws_config.bucket_name,
    aws_access_key_id=aws_config.aws_access_key_id,
    aws_secret_access_key=aws_config.aws_secret_access_key,
    region_name=aws_config.region_name
)

# Load data
print("\nLoading data...")
df = loader.load_nasdaq_data(s3_key=aws_config.s3_key, use_cache=False)

print(f"\n✅ SUCCESS!")
print(f"\nDataFrame Info:")
print(f"  Shape: {df.shape}")
print(f"  Index: {df.index.names}")
print(f"  Columns: {list(df.columns)}")
print(f"\nFirst few rows:")
print(df.head())
print(f"\nSample tickers: {df.index.get_level_values('ticker').unique()[:10].tolist()}")
