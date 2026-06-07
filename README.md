# RAG-powered-AI-agent

Full-stack Retrieval-Augmented Generation (RAG) AI agent with FastAPI + React, OpenAI, LangChain, and ChromaDB.

## Features

- FastAPI backend with JWT authentication
- React frontend with responsive dashboard and chat
- Upload/index PDF, TXT, DOCX documents
- OpenAI embeddings + ChromaDB vector search
- LangChain orchestration for context-aware responses
- Streaming chat responses with source citations
- Conversation memory (chat history persisted per user)
- File management dashboard (list/delete)
- Docker and docker-compose support

## Project structure

```text
backend/
  app/
    core/        # config + security
    models/      # SQLAlchemy entities
    routers/     # auth, documents, chat APIs
    services/    # document parsing + RAG orchestration
    tests/       # focused backend tests
frontend/
  src/           # React app (auth, dashboard, chat)
sample_documents/
```

## Environment setup

1. Copy `.env.example` to `.env`
2. Set `OPENAI_API_KEY`

## Local development

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173`, backend at `http://localhost:8000`.

## API endpoints

- `POST /api/auth/register`
- `POST /api/auth/login`
- `POST /api/documents/upload`
- `POST /api/documents/{document_id}/index`
- `GET /api/documents/`
- `DELETE /api/documents/{document_id}`
- `GET /api/chat/history`
- `POST /api/chat/stream` (SSE stream)

## Docker

```bash
docker compose up --build
```

## Testing

```bash
cd backend
pytest app/tests -q
```

## Sample files

Use files in `sample_documents/` to test indexing and chat.
