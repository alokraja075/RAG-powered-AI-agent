from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    app_name: str = 'RAG AI Agent API'
    openai_api_key: str = Field(default='')
    openai_model: str = Field(default='gpt-4o-mini')
    embedding_model: str = Field(default='text-embedding-3-small')
    secret_key: str = Field(default='change-me-in-production')
    access_token_expire_minutes: int = Field(default=60 * 24)
    database_url: str = Field(default='sqlite:///./data/app.db')
    chroma_persist_directory: str = Field(default='./data/chroma')
    upload_directory: str = Field(default='./data/uploads')
    cors_origins: str = Field(default='http://localhost:5173')


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
