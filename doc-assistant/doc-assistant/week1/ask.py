# week1/ask.py
# This script sends a question to Claude via Amazon Bedrock and prints the answer.

import os
import json
import boto3
from dotenv import load_dotenv
from botocore.exceptions import ClientError

# Load project .env (doc-assistant/.env) so env vars like INFERENCE_PROFILE_ARN are picked up
script_dir = os.path.dirname(__file__)
project_env = os.path.normpath(os.path.join(script_dir, "..", "..", ".env"))
load_dotenv(project_env)

# Bedrock client and model configuration
client = boto3.client("bedrock-runtime", region_name=os.getenv("AWS_REGION", "us-east-1"))
MODEL_ID = os.getenv("MODEL_ID", "anthropic.claude-3-5-sonnet-20241022-v2:0")

def ask_claude(question: str) -> str:
    """
    Send a question to Claude and return the answer as a string.
    
    question: str  — the user's question (a string)
    return:   str  — Claude's answer (a string)
    """
    
    # Bedrock expects a specific JSON structure — this is the "messages" format
    # Each message is a dict with "role" (who is speaking) and "content" (what they said)
    messages = [
        {
            "role": "user",
            "content": question   # the user's question goes here
        }
    ]
    
    # Build the full request body as a Python dict
    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1024,        # maximum number of tokens in the response
        "messages": messages
    }
    
    # Prefer an inference profile ARN/ID if provided, otherwise use MODEL_ID
    model_to_use = os.getenv("INFERENCE_PROFILE_ARN") or MODEL_ID

    # Call Bedrock — json.dumps() converts the Python dict to a JSON string
    response = client.invoke_model(
        modelId=model_to_use,
        body=json.dumps(request_body).encode("utf-8")
    )
    
    # response["body"] is a stream — .read() gets the bytes, json.loads() parses it
    response_body = json.loads(response["body"].read())
    
    # The answer text is nested inside content[0]["text"]
    answer = response_body["content"][0]["text"]
    
    return answer


# This block only runs when you execute this file directly (not when imported)
if __name__ == "__main__":
    question = input("Ask anything: ")   # input() waits for the user to type
    
    print("\nClaude says:")
    answer = ask_claude(question)
    print(answer)