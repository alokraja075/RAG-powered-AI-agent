# Week 4: Chunk Text + Generate Embeddings

This folder contains a small script that:

1. Extracts text from the PDF.
2. Splits the text into overlapping token chunks with `tiktoken`.
3. Sends each chunk to Amazon Bedrock Titan Embeddings v2.
4. Prints the first 5 numbers of each embedding vector.

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
