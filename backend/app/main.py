"""
Prompt Master Backend
Main FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api import prompts_router, projects_router, history_router
from app.api.models import HealthResponse
from app.agents import AGENT_REGISTRY


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup/shutdown events."""
    # Startup
    print("🚀 Prompt Master API starting up...")
    print(f"📦 Loaded {len(AGENT_REGISTRY)} agents: {list(AGENT_REGISTRY.keys())}")
    
    # Validate Supabase configuration
    from app.core.config import get_settings
    settings = get_settings()
    
    if not settings.supabase_url or not settings.supabase_service_key:
        print("⚠️  WARNING: Supabase credentials not fully configured!")
        print(f"  - SUPABASE_URL: {'✓' if settings.supabase_url else '✗ Missing'}")
        print(f"  - SUPABASE_SERVICE_KEY: {'✓' if settings.supabase_service_key else '✗ Missing'}")
    else:
        print("✓ Supabase configuration validated")
    
    yield
    
    # Shutdown
    print("👋 Prompt Master API shutting down...")


# Create FastAPI application
app = FastAPI(
    title="Prompt Master API",
    description="Multi-Agent Prompt Optimizer with LangGraph",
    version="1.0.0",
    lifespan=lifespan
)

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
