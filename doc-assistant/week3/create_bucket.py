import boto3
import os
from dotenv import load_dotenv
script_dir = os.path.dirname(__file__)
project_env = os.path.normpath(os.path.join(script_dir, "..", ".env"))
load_dotenv(project_env)
s3=boto3.client("s3",region_name=os.getenv("AWS_REGION"))
S3_BUCKET_NAME="doc-assistant-bucket-michael"
bucket_name=os.getenv("S3_BUCKET_NAME", S3_BUCKET_NAME)
region=os.getenv("AWS_REGION")
try:
    if region=="us-east-1":
        s3.create_bucket(Bucket=bucket_name)
    else:
        s3.create_bucket(
            Bucket=bucket_name, 
            CreateBucketConfiguration={'LocationConstraint': region}
        )
    s3.put_public_access_block(
        Bucket=bucket_name, 
        PublicAccessBlockConfiguration={
            'BlockPublicAcls': True,
            'IgnorePublicAcls': True,
            'BlockPublicPolicy': True,
            'RestrictPublicBuckets': True
        }
    )
except Exception as e:
    print(e)
print(f"Bucket created: {bucket_name}")
