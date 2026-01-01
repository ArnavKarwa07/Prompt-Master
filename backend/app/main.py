"""
Prompt Master Backend
Main FastAPI application entry point.
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.api import prompts_router, projects_router, history_router
from app.api.models import HealthResponse
from app.agents import AGENT_REGISTRY


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup/shutdown events."""
    # Startup - minimal logging
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Prompt Master API starting - loaded {len(AGENT_REGISTRY)} agents")
    
    # Validate Supabase configuration
    from app.core.config import get_settings
    settings = get_settings()
    
    if not settings.supabase_url or not settings.supabase_service_key:
        logger.warning("Supabase credentials not fully configured")
    
    yield
    
    # Shutdown
    logger.info("Prompt Master API shutting down")


# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Create FastAPI application
app = FastAPI(
    title="Prompt Master API",
    description="Multi-Agent Prompt Optimizer with LangGraph",
    version="1.0.0",
    lifespan=lifespan
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://*.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(prompts_router, prefix="/api/v1")
app.include_router(projects_router, prefix="/api/v1")
app.include_router(history_router, prefix="/api/v1")


@app.get("/", tags=["root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Prompt Master API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        agents_available=list(AGENT_REGISTRY.keys())
    )


if __name__ == "__main__":
    import uvicorn
    from app.core.config import get_settings
    
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
