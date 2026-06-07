import argparse
import json
import os
from typing import List

import boto3
try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional dependency
    def load_dotenv(*_args, **_kwargs):
        return False


script_dir = os.path.dirname(__file__)
project_env = os.path.normpath(os.path.join(script_dir, "..", ".env"))
load_dotenv(project_env)


def chunk_text(text: str, chunk_tokens: int = 500, overlap_tokens: int = 50) -> List[str]:
    if chunk_tokens <= 0:
        raise ValueError("chunk_tokens must be > 0")
    if overlap_tokens < 0:
        raise ValueError("overlap_tokens must be >= 0")
    if overlap_tokens >= chunk_tokens:
        raise ValueError("overlap_tokens must be smaller than chunk_tokens")

    tokens = text.split()
    if not tokens:
        return []

    chunks: List[str] = []
    step = chunk_tokens - overlap_tokens
    for start in range(0, len(tokens), step):
        end = start + chunk_tokens
        chunk = " ".join(tokens[start:end]).strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(tokens):
            break
    return chunks


def embed_chunk(client, chunk: str, model_id: str) -> List[float]:
    response = client.invoke_model(
        modelId=model_id,
        body=json.dumps({"inputText": chunk}).encode("utf-8"),
    )
    payload = json.loads(response["body"].read())
    if "embedding" in payload:
        return payload["embedding"]
    return payload["embeddingsByType"]["float"]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Split document text into overlapping chunks and embed each chunk with Titan."
    )
    parser.add_argument("--file", help="Path to a text file to embed.")
    parser.add_argument("--text", help="Raw text to embed.")
    parser.add_argument("--chunk-size", type=int, default=500, help="Chunk size in tokens (word-based).")
    parser.add_argument("--overlap", type=int, default=50, help="Overlap in tokens (word-based).")
    parser.add_argument("--model-id", default="amazon.titan-embed-text-v2:0")
    parser.add_argument("--region", default=os.getenv("AWS_REGION", "us-east-1"))
    args = parser.parse_args()

    if not args.file and not args.text:
        parser.error("Provide --file or --text.")

    text = args.text
    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            text = f.read()

    chunks = chunk_text(text or "", chunk_tokens=args.chunk_size, overlap_tokens=args.overlap)
    if not chunks:
        print("No text to embed.")
        return

    client = boto3.client("bedrock-runtime", region_name=args.region)
    print(f"Created {len(chunks)} chunks. Embedding each chunk with {args.model_id}...\n")

    for i, chunk in enumerate(chunks, start=1):
        vector = embed_chunk(client, chunk, args.model_id)
        print(f"Chunk {i}: vector length={len(vector)}, first5={vector[:5]}")

    print(
        "\nWhy this matters: embeddings turn text into numeric vectors; chunking with overlap preserves context across boundaries for better retrieval."
    )


if __name__ == "__main__":
    main()
