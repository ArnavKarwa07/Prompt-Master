"""API routes module."""
from app.api.routes.prompts import router as prompts_router
from app.api.routes.projects import router as projects_router
from app.api.routes.history import router as history_router

__all__ = ["prompts_router", "projects_router", "history_router"]
