import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Gemini Configuration
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"

    # Server Settings
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Knowledge Base & Vector Database Settings (Q2)
    CHROMA_PERSIST_DIR: str = "./q2_knowledge_base/data/chroma"
    HYBRID_RETRIEVAL_ALPHA: float = 0.5
    TOP_K_RETRIEVAL: int = 5
    SUFFICIENCY_THRESHOLD: float = 0.01

    # Optional & Future Service Integrations
    VAPI_API_KEY: Optional[str] = os.getenv("VAPI_API_KEY")
    VAPI_PUBLIC_KEY: Optional[str] = os.getenv("VAPI_PUBLIC_KEY")
    DEEPGRAM_API_KEY: Optional[str] = None
    LANGSMITH_API_KEY: Optional[str] = None
    LANGSMITH_PROJECT: Optional[str] = "ai-engineer-assessment"
    LANGSMITH_TRACING: bool = False
    COHERE_API_KEY: Optional[str] = None
    ELEVENLABS_API_KEY: Optional[str] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()
