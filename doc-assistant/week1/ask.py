# week1/ask.py
# This script sends a question to Claude via Amazon Bedrock and prints the answer.

import os
import json
import boto3
from dotenv import load_dotenv
from botocore.exceptions import ClientError

# Load project .env (doc-assistant/.env) so env vars like INFERENCE_PROFILE_ARN are picked up
script_dir = os.path.dirname(__file__)
project_env = os.path.normpath(os.path.join(script_dir, "..", ".env"))
load_dotenv(project_env)

# Bedrock client and model configuration
client = boto3.client("bedrock-runtime", region_name=os.getenv("AWS_REGION", "us-east-1"))
MODEL_ID = os.getenv("MODEL_ID", "anthropic.claude-opus-4-5-20251101-v1:0")

def ask_claude(question: str) -> str:
    messages = [
        {
            "role": "user",
            "content": question    
        }
    ]  
    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1024,       
        "messages": messages
    }
    
    use_inference_profile = os.getenv("USE_INFERENCE_PROFILE", "").lower() in {"1", "true", "yes"}
    model_to_use = os.getenv("INFERENCE_PROFILE_ARN") if use_inference_profile else MODEL_ID
    response = client.invoke_model(
        modelId=model_to_use,
        body=json.dumps(request_body).encode("utf-8")
    )
    response_body = json.loads(response["body"].read())
    answer = response_body["content"][0]["text"]
    return answer


# This block only runs when you execute this file directly (not when imported)
if __name__ == "__main__":
    question = input("Ask anything: ")   # input() waits for the user to type
    
    print("\nClaude says:")
    answer = ask_claude(question)
    print(answer)