import os
import argparse
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv


script_dir = os.path.dirname(__file__)
project_env = os.path.normpath(os.path.join(script_dir, "..", ".env"))
load_dotenv(project_env)

parser = argparse.ArgumentParser()
parser.add_argument("--file", default="India_Article.pdf", help="India_15_Page_Article.pdf")
args = parser.parse_args()

s3 = boto3.client("s3", region_name=os.getenv("AWS_REGION", "us-east-1"))
S3_BUCKET_NAME = "doc-assistant-bucket-michael"
bucket_name = os.getenv("S3_BUCKET_NAME", S3_BUCKET_NAME)
region = os.getenv("AWS_REGION", "us-east-1")

file_path = args.file if os.path.isabs(args.file) else os.path.join(script_dir, args.file)
file_name = os.path.basename(file_path)
with open(file_path, "rb") as f:
    body = f.read()

try:
    s3.put_object(
        Bucket=bucket_name,
        Key=f"documents/{file_name}",
        Body=body,
    )
except ClientError as error:
    if error.response["Error"]["Code"] != "NoSuchBucket":
        raise
    if region == "us-east-1":
        s3.create_bucket(Bucket=bucket_name)
    else:
        s3.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={"LocationConstraint": region},
        )
    s3.put_object(
        Bucket=bucket_name,
        Key=f"documents/{file_name}",
        Body=body,
    )

print(f"Uploaded: documents/{file_name}")