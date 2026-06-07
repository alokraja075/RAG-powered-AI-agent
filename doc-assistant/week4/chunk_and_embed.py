import argparse
import json
import os
from pathlib import Path

import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
from PyPDF2 import PdfReader
import tiktoken


script_dir = Path(__file__).resolve().parent
project_env = script_dir.parent / ".env"
load_dotenv(project_env)

parser = argparse.ArgumentParser(description="Chunk PDF text and generate Titan embeddings for each chunk.")
parser.add_argument(
    "--file",
    default="../week3/India_15_Page_Article.pdf",
    help="PDF file path relative to week4, or an absolute path",
)
parser.add_argument("--chunk-size", type=int, default=500, help="Chunk size in tokens")
parser.add_argument("--overlap", type=int, default=50, help="Token overlap between chunks")
parser.add_argument("--max-chunks", type=int, default=0, help="Optional limit for quick testing")
args = parser.parse_args()


def resolve_path(file_arg: str) -> Path:
    file_path = Path(file_arg)
    if file_path.is_absolute():
        return file_path
    return (script_dir / file_path).resolve()


def extract_text_from_pdf(pdf_path: Path) -> str:
    reader = PdfReader(str(pdf_path))
    return "\n\n".join(page.extract_text() or "" for page in reader.pages)


def chunk_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    if chunk_size <= 0:
        raise ValueError("chunk-size must be greater than zero")
    if overlap < 0:
        raise ValueError("overlap cannot be negative")
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk-size")

    step = chunk_size - overlap
    try:
        encoder = tiktoken.get_encoding("cl100k_base")
        tokens = encoder.encode(text)
        token_chunks = [tokens[i : i + chunk_size] for i in range(0, len(tokens), step)]
        return [encoder.decode(chunk) for chunk in token_chunks]
    except Exception:
        words = text.split()
        word_chunks = [words[i : i + chunk_size] for i in range(0, len(words), step)]
        return [" ".join(chunk) for chunk in word_chunks]


def get_embedding(client, chunk: str) -> list[float]:
    model_id = os.getenv("EMBEDDING_MODEL_ID", "amazon.titan-embed-text-v2:0")
    body = {"inputText": chunk}
    response = client.invoke_model(
        modelId=model_id,
        body=json.dumps(body).encode("utf-8"),
        contentType="application/json",
        accept="application/json",
    )
    response_body = json.loads(response["body"].read())
    return response_body["embedding"]


def main() -> None:
    pdf_path = resolve_path(args.file)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    text = extract_text_from_pdf(pdf_path)
    if not text.strip():
        raise ValueError("No text could be extracted from the PDF")

    chunks = chunk_text(text, args.chunk_size, args.overlap)
    if args.max_chunks > 0:
        chunks = chunks[: args.max_chunks]

    print(f"PDF: {pdf_path}")
    print(f"Chunks: {len(chunks)}")

    client = boto3.client("bedrock-runtime", region_name=os.getenv("AWS_REGION", "us-east-1"))

    for index, chunk in enumerate(chunks, start=1):
        embedding = get_embedding(client, chunk)
        preview = embedding[:5]
        print(f"Chunk {index}: first 5 embedding values = {preview}")


if __name__ == "__main__":
    main()
