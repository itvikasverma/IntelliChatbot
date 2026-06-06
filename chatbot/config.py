from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    groq_api_key: str = Field(..., alias="GROQ_API_KEY")
    groq_model: str = Field("llama-3.3-70b-versatile", alias="GROQ_MODEL")
    embedding_model: str = Field("BAAI/bge-small-en-v1.5", alias="EMBEDDING_MODEL")

    qdrant_url: str = Field("http://localhost:6333", alias="QDRANT_URL")
    qdrant_api_key: str | None = Field(None, alias="QDRANT_API_KEY")
    qdrant_collection: str = Field("personal_memory", alias="QDRANT_COLLECTION")
    qdrant_timeout: int = Field(60, alias="QDRANT_TIMEOUT")

    chatbot_system_prompt: str = Field(
        "You are a helpful assistant. Use tools when they improve factual accuracy. "
        "Prefer the personal data RAG tool for personal or user-specific facts.",
        alias="CHATBOT_SYSTEM_PROMPT",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
