"""
Test script to verify S3 caching performance
"""
import time
from s3_data_loader import S3DataLoader
from config import AWSConfig

print("=" * 70)
print("S3 CACHING PERFORMANCE TEST")
print("=" * 70)

aws_config = AWSConfig()

# Test 1: Fresh load (should download from S3)
print("\n[TEST 1] Fresh Load (no cache)")
print("-" * 70)
import os
if os.path.exists("NASDAQ.csv"):
    os.remove("NASDAQ.csv")
    print("Removed existing cache file")

loader = S3DataLoader(
    bucket_name=aws_config.bucket_name,
    aws_access_key_id=aws_config.aws_access_key_id,
    aws_secret_access_key=aws_config.aws_secret_access_key,
    region_name=aws_config.region_name
)

start = time.time()
df1 = loader.load_nasdaq_data(aws_config.s3_key, use_cache=True)
time1 = time.time() - start

print(f"\n⏱️  Time: {time1:.2f} seconds")
print(f"📊 Loaded: {len(df1):,} rows")

# Test 2: Cached load (should use local file)
print("\n[TEST 2] Cached Load (using local file)")
print("-" * 70)

start = time.time()
df2 = loader.load_nasdaq_data(aws_config.s3_key, use_cache=True)
time2 = time.time() - start

print(f"\n⏱️  Time: {time2:.2f} seconds")
print(f"📊 Loaded: {len(df2):,} rows")

# Performance comparison
print("\n" + "=" * 70)
print("PERFORMANCE SUMMARY")
print("=" * 70)
print(f"Fresh Load (S3):     {time1:.2f}s")
print(f"Cached Load (Local): {time2:.2f}s")
print(f"Speed improvement:   {time1/time2:.1f}x faster")
print(f"Time saved:          {time1-time2:.2f}s ({((time1-time2)/time1*100):.1f}%)")
print("=" * 70)
