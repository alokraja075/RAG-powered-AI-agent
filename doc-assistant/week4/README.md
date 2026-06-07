# Week 4: Chunk Text + Generate Embeddings

This folder contains a small script that:

1. Extracts text from the PDF.
2. Splits the text into overlapping token chunks with `tiktoken`.
3. Sends each chunk to Amazon Bedrock Titan Embeddings v2.
4. Prints the first 5 numbers of each embedding vector.

## What you'll learn

- What embeddings are and why chunking matters for retrieval quality.
- How to call `amazon.titan-embed-text-v2:0` with `boto3` (`bedrock-runtime`).
- The shape of an embedding vector and how to inspect it quickly.

## Run

From `doc-assistant`:

```bash
./venv/bin/python week4/chunk_and_embed.py
```

Optional arguments:

```bash
./venv/bin/python week4/chunk_and_embed.py --file ../week3/India_15_Page_Article.pdf --chunk-size 500 --overlap 50 --max-chunks 2
```

## Dependencies

Install the shared requirements with:

```bash
./venv/bin/pip install -r requirements.txt
```
