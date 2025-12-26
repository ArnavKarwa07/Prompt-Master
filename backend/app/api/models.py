"""
API Models
Pydantic models for API request/response schemas.
"""
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


# ============ Request Models ============

class OptimizePromptRequest(BaseModel):
    """Request to optimize a prompt."""
    prompt: str = Field(..., min_length=1, max_length=10000, description="The prompt to optimize")
    goal: str = Field(..., min_length=1, max_length=1000, description="What the user wants to achieve")
    force_agent: Optional[Literal["coding", "creative", "analyst", "general"]] = Field(
        None, description="Force a specific agent instead of auto-routing"
    )
    project_id: Optional[str] = Field(None, description="Project ID for saving history (authenticated users only)")


class CreateProjectRequest(BaseModel):
    """Request to create a new project."""
    name: str = Field(..., min_length=1, max_length=100, description="Project name")


class UploadContextRequest(BaseModel):
    """Request to upload context files."""
    project_id: str = Field(..., description="Project to add context to")


# ============ Response Models ============

class RoutingInfo(BaseModel):
    """Information about agent routing decision."""
    confidence: float = Field(..., ge=0, le=1)
    reasoning: str


class OptimizePromptResponse(BaseModel):
    """Response from prompt optimization."""
    original_prompt: str
    goal: str
    agent: str
    routing: RoutingInfo
    score: int = Field(..., ge=0, le=100)
    feedback: str
    optimized_prompt: str
    error: Optional[str] = None


class ProjectResponse(BaseModel):
    """Project data response."""
    id: str
    name: str
    created_at: Optional[datetime] = None


class ProjectListResponse(BaseModel):
    """List of projects response."""
    projects: list[ProjectResponse]


class PromptHistoryItem(BaseModel):
    """Single prompt history entry."""
    id: str
    prompt_text: str
    agent_used: str
    score: int
    optimized_prompt: Optional[str] = None
    created_at: Optional[datetime] = None


class PromptHistoryResponse(BaseModel):
    """Prompt history response."""
    history: list[PromptHistoryItem]


class AgentInfo(BaseModel):
    """Information about an available agent."""
    name: str
    description: str


class AgentsListResponse(BaseModel):
    """List of available agents."""
    agents: list[AgentInfo]


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    agents_available: list[str]
