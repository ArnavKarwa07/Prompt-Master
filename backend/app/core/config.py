"""
Application Configuration Module
Handles all environment variables and settings for the Prompt Master backend.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Keys
    groq_api_key: str
    
    # Supabase
    supabase_url: str
    supabase_anon_key: str
    supabase_service_key: str
    
    # Clerk Auth
    clerk_secret_key: str
    clerk_publishable_key: str
    clerk_jwks_url: str
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    
    # LLM Models (Groq)
    primary_model: str = "llama-3.3-70b-versatile"
    secondary_model: str = "llama-3.1-8b-instant"
    
    # Vector Configuration
    embedding_dimension: int = 1536
    max_chunk_size: int = 500
    chunk_overlap: int = 50
    
    # Storage
    storage_bucket: str = "user-files"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance."""
    return Settings()
