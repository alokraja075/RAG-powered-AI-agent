import os
import json
import argparse
import textwrap

import boto3
from dotenv import load_dotenv
from PyPDF2 import PdfReader


script_dir = os.path.dirname(__file__)
project_env = os.path.normpath(os.path.join(script_dir, "..", ".env"))
load_dotenv(project_env)


parser = argparse.ArgumentParser(description="Ask an AI question about a PDF stored in S3 (or local week3 folder).")
parser.add_argument("--file", default="India_15_Page_Article.pdf", help="PDF filename in week3 or in S3 documents/")
parser.add_argument("--question", help="Question to ask the model. If omitted, you'll be prompted.")
parser.add_argument("--max-context-chars", type=int, default=30000, help="Max chars of extracted context to send")
args = parser.parse_args()


def extract_text_from_pdf(local_path: str) -> str:
    reader = PdfReader(local_path)
    pages_text = [page.extract_text() or "" for page in reader.pages]
    return "\n\n".join(pages_text)


def main():
    local_pdf = os.path.join(script_dir, args.file) if not os.path.isabs(args.file) else args.file

    # ensure file exists locally; if not, try downloading from S3
    if not os.path.exists(local_pdf):
        s3 = boto3.client("s3", region_name=os.getenv("AWS_REGION", "us-east-1"))
        bucket = os.getenv("S3_BUCKET_NAME", "doc-assistant-bucket-michael")
        key = f"documents/{args.file}"
        try:
            resp = s3.get_object(Bucket=bucket, Key=key)
            with open(local_pdf, "wb") as out:
                out.write(resp["Body"].read())
            print(f"Downloaded {key} from s3://{bucket} to {local_pdf}")
        except Exception as e:
            print(f"Failed to retrieve {key} from bucket {bucket}: {e}")
            return

    extracted = extract_text_from_pdf(local_pdf)
    if not extracted.strip():
        print("No text extracted from PDF.")
        return

    # shorten context if necessary
    context = (extracted[: args.max_context_chars]) if len(extracted) > args.max_context_chars else extracted

    question = args.question or input("Question: ")

    # compose messages: put extracted text as system/context
    messages = [
        {"role": "system", "content": f"You are given the following document context:\n\n{context}"},
        {"role": "user", "content": question},
    ]

    client = boto3.client("bedrock-runtime", region_name=os.getenv("AWS_REGION", "us-east-1"))
    use_inference_profile = os.getenv("USE_INFERENCE_PROFILE", "").lower() in {"1", "true", "yes"}
    model_to_use = os.getenv("INFERENCE_PROFILE_ARN") if use_inference_profile else os.getenv("MODEL_ID", "anthropic.claude-opus-4-5-20251101-v1:0")

    # Bedrock Messages API expects a top-level `system` field (not a message role).
    system_content = None
    user_messages = []
    for m in messages:
        if m.get("role") == "system":
            system_content = m.get("content")
        else:
            user_messages.append(m)

    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1024,
        "messages": user_messages,
    }
    if system_content is not None:
        request_body["system"] = system_content

    resp = client.invoke_model(modelId=model_to_use, body=json.dumps(request_body).encode("utf-8"))
    resp_body = json.loads(resp["body"].read())
    # model response format: content[0].text
    answer = resp_body.get("content", [{}])[0].get("text")
    print("\n--- Model answer ---\n")
    print(answer)


if __name__ == "__main__":
    main()
