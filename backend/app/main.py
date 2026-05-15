from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.db import Base, engine
from app.models import entities  # noqa: F401
from app.routers import auth, documents, chat


settings = get_settings()
Path(settings.upload_directory).mkdir(parents=True, exist_ok=True)
Path(settings.chroma_persist_directory).mkdir(parents=True, exist_ok=True)
Path('./data').mkdir(parents=True, exist_ok=True)
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_origins.split(',') if origin.strip()],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.get('/health')
def health():
    return {'status': 'ok'}


app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(chat.router)
