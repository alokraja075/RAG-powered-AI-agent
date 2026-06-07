import os
import argparse
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
from PyPDF2 import PdfReader

script_dir = os.path.dirname(__file__)
project_env = os.path.normpath(os.path.join(script_dir, "..", ".env"))
load_dotenv(project_env)
parser = argparse.ArgumentParser()
parser.add_argument("--file", default="India_15_Page_Article.pdf", help="India_15_Page_Article.pdf")
args = parser.parse_args()
s3 = boto3.client("s3", region_name=os.getenv("AWS_REGION", "us-east-1"))
S3_BUCKET_NAME = "doc-assistant-bucket-michael"
bucket_name = os.getenv("S3_BUCKET_NAME", S3_BUCKET_NAME)
region = os.getenv("AWS_REGION", "us-east-1")
response = s3.get_object(Bucket=bucket_name, Key=f"documents/{args.file}")
body = response["Body"].read()

# save to local file inside week3 so PdfReader can open it
local_path = os.path.join(script_dir, args.file)
with open(local_path, "wb") as out:
	out.write(body)

reader = PdfReader(local_path)
text = "\n\n".join(page.extract_text() or "" for page in reader.pages)
print(text)