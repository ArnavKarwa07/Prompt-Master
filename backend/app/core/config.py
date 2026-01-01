"""
Application Configuration Module
Handles all environment variables and settings for the Prompt Master backend.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables.
    All keys are optional to allow the server to start; individual services
    will validate their required keys at runtime.
    """
    
    # API Keys (optional; validated where used)
    groq_api_key: Optional[str] = None
    
    # Supabase (service role used server-side)
    supabase_url: Optional[str] = None
    supabase_anon_key: Optional[str] = None
    supabase_service_key: Optional[str] = None
    
    # Clerk Auth (validated only on protected routes)
    clerk_secret_key: Optional[str] = None
    clerk_publishable_key: Optional[str] = None
    clerk_jwks_url: Optional[str] = None
    
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
