import os
import json
import sys
import boto3
from dotenv import load_dotenv


script_dir = os.path.dirname(__file__)
project_env = os.path.normpath(os.path.join(script_dir, "..", ".env"))
load_dotenv(project_env)


def get_bedrock_client():
    client = boto3.client(
        service_name="bedrock-runtime",
        region_name=os.getenv("AWS_REGION", "us-east-1")
    )
    return client


def stream_response(client, messages: list) -> str:
    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1024,
        "system": "You are a helpful enterprise document assistant. Answer clearly and concisely.",
        "messages": messages    
    }
    print("Payload sent to AWS:")
    print(json.dumps(request_body, indent=2))
    response = client.invoke_model_with_response_stream(
        modelId=os.getenv("INFERENCE_PROFILE_ARN") or os.getenv("MODEL_ID", "anthropic.claude-sonnet-4-6"),
        body=json.dumps(request_body).encode("utf-8")
    )

    full_reply = ""   

    for event in response["body"]:
        chunk = json.loads(event["chunk"]["bytes"].decode("utf-8"))
        if chunk.get("type") == "content_block_delta":
            token = chunk["delta"].get("text", "")
            print(token, end="", flush=True)    
            full_reply += token                 

    print()    
    return full_reply