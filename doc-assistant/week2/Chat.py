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

def main():
    print("Enterprise Doc Assistant — Week 2")
    print("Type your message and press Enter. Type 'quit' to exit.\n")
    client = get_bedrock_client()
    memory = []
    while True:  
        user_input = input("You: ").strip()  
        if user_input.lower() == "quit":
            print("Goodbye!")
            break
        if not user_input:
            continue

        memory.append({
            "role": "user",
            "content": user_input
        })

        print("Assistant: ", end="", flush=True)
        answer = ask_claude(client, memory)
        print()

        memory.append({
            "role": "assistant",
            "content": answer
        })
        
def ask_claude(client, messages: list) -> str:
    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1024,       
        "messages": messages
    }
    print("Payload sent to AWS:")
    print(json.dumps(request_body, indent=2))
    use_inference_profile = os.getenv("USE_INFERENCE_PROFILE", "").lower() in {"1", "true", "yes"}
    model_to_use = os.getenv("INFERENCE_PROFILE_ARN") if use_inference_profile else os.getenv("MODEL_ID", "anthropic.claude-sonnet-4-6")
    response = client.invoke_model_with_response_stream(
        modelId=model_to_use,
        body=json.dumps(request_body).encode("utf-8")
    )

    answer = ""
    for event in response["body"]:
        if "chunk" not in event:
            continue

        chunk = json.loads(event["chunk"]["bytes"].decode("utf-8"))
        if chunk.get("type") == "content_block_delta":
            token = chunk["delta"].get("text", "")
            sys.stdout.write(token)
            sys.stdout.flush()
            answer += token

    return answer

if __name__ == "__main__":
    main()