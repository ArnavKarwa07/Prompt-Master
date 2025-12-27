"""
Prompt Routes
API endpoints for prompt optimization.
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
import logging

from app.api.models import (
    OptimizePromptRequest,
    OptimizePromptResponse,
    RoutingInfo,
    AgentsListResponse,
    AgentInfo
)
from app.core.auth import get_optional_user, ClerkUser
from app.core.supabase_client import get_supabase_service, SupabaseService
from app.graph import run_prompt_optimization
from app.agents import AGENT_REGISTRY

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/prompts", tags=["prompts"])


@router.post("/optimize", response_model=OptimizePromptResponse)
async def optimize_prompt(
    request: OptimizePromptRequest,
    user: Optional[ClerkUser] = Depends(get_optional_user),
    supabase: SupabaseService = Depends(get_supabase_service)
):
    """
    Optimize a prompt using the multi-agent system.
    
    - **Guest Mode**: No authentication required, results not saved
    - **User Mode**: Optionally save to project history
    """
    # Run the optimization workflow
    result = await run_prompt_optimization(
        prompt=request.prompt,
        goal=request.goal,
        force_agent=request.force_agent,
        use_rag=True,
        user_id=user.id if user else None,
        project_id=request.project_id
    )
    
    # If authenticated and project_id provided, save to history
    if user and request.project_id and not result.get("error"):
        try:
            # Verify project belongs to user
            project = await supabase.get_project(request.project_id)
            if project:
                # Map Clerk user ID to DB UUID v5 for comparison
                import uuid
                db_user_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"clerk:{user.id}"))
                if project.get("user_id") != db_user_id:
                    raise Exception("Access denied: project does not belong to user")
                await supabase.save_prompt_history(
                    project_id=request.project_id,
                    prompt_text=request.prompt,
                    agent_used=result["agent"],
                    score=result["score"],
                    optimized_prompt=result["optimized_prompt"]
                )
                # Enforce global cap of 10 history entries across all projects
                try:
                    await supabase.enforce_global_prompt_cap(user.id, 10)
                except Exception as cap_err:
                    logger.warning(f"Failed to enforce global history cap: {str(cap_err)}")
        except ValueError as e:
            # Log API key errors but don't fail the optimization
            logger.warning(f"Failed to save prompt history due to authentication: {str(e)}")
        except Exception as e:
            # Log other errors but don't fail the optimization
            logger.warning(f"Failed to save prompt history: {str(e)}")
    
    return OptimizePromptResponse(
        original_prompt=result["prompt"],
        goal=result["goal"],
        agent=result["agent"],
        routing=RoutingInfo(
            confidence=result["routing"]["confidence"],
            reasoning=result["routing"]["reasoning"]
        ),
        score=result["score"],
        feedback=result["feedback"],
        optimized_prompt=result["optimized_prompt"],
        error=result.get("error")
    )


@router.get("/agents", response_model=AgentsListResponse)
async def list_agents():
    """List all available specialized agents."""
    agents = []
    for name, cls in AGENT_REGISTRY.items():
        agent_instance = cls()
        agents.append(AgentInfo(
            name=name,
            description=agent_instance.description
        ))
    
    return AgentsListResponse(agents=agents)


@router.post("/analyze-only")
async def analyze_prompt(
    request: OptimizePromptRequest,
    user: Optional[ClerkUser] = Depends(get_optional_user)
):
    """
    Quick analysis without full optimization.
    Returns just the routing decision and basic scoring.
    """
    from app.graph.supervisor import get_supervisor
    
    supervisor = get_supervisor()
    routing = await supervisor.classify(request.prompt, request.goal)
    
    return {
        "prompt": request.prompt,
        "goal": request.goal,
        "recommended_agent": routing["agent"],
        "confidence": routing["confidence"],
        "reasoning": routing["reasoning"]
    }
