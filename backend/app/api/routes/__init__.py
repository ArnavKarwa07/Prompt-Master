"""API routes module."""
from app.api.routes.prompts import router as prompts_router
from app.api.routes.projects import router as projects_router

__all__ = ["prompts_router", "projects_router"]
