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
# @limiter.limit("10/minute")  # Uncomment to enable rate limiting
async def optimize_prompt(
    request: OptimizePromptRequest,
    user: Optional[ClerkUser] = Depends(get_optional_user),
    supabase: SupabaseService = Depends(get_supabase_service)
):
    """
    Optimize a prompt using the multi-agent system.
    
    - **Guest Mode**: No authentication required, results not saved
    - **User Mode**: Always save to history (with optional project association)
    """
    print(f"[OPTIMIZE] user: {user.id if user else 'guest'}, project_id: {request.project_id}")
    
    # Run the optimization workflow
    result = await run_prompt_optimization(
        prompt=request.prompt,
        goal=request.goal,
        force_agent=request.force_agent,
        use_rag=True,
        user_id=user.id if user else None,
        project_id=request.project_id
    )
    
    # If authenticated, ALWAYS save to history (project_id is optional)
    if user and not result.get("error"):
        print(f"[OPTIMIZE] Saving prompt to history for user {user.id}")
        try:
            # If project_id provided, verify it belongs to user
            project_name = None
            if request.project_id:
                project = await supabase.get_project(request.project_id)
                if project:
                    import uuid
                    db_user_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"clerk:{user.id}"))
                    if project.get("user_id") != db_user_id:
                        print(f"[OPTIMIZE] Project doesn't belong to user, saving without project")
                        request.project_id = None
                    else:
                        project_name = project.get("name")
                else:
                    print(f"[OPTIMIZE] Project not found, saving without project")
                    request.project_id = None
            
            # Save to history (project_id can be None)
            await supabase.save_prompt_history_v2(
                user_id=user.id,
                prompt_text=request.prompt,
                agent_used=result["agent"],
                score=result["score"],
                optimized_prompt=result["optimized_prompt"],
                project_id=request.project_id,
                project_name=project_name
            )
            print(f"[OPTIMIZE] Successfully saved prompt to history")
            
            # Enforce global cap of 10 history entries
            try:
                await supabase.enforce_global_prompt_cap_v2(user.id, 10)
            except Exception as cap_err:
                print(f"[OPTIMIZE] Failed to enforce global history cap: {str(cap_err)}")
        except ValueError as e:
            print(f"[OPTIMIZE] Failed to save prompt history due to authentication: {str(e)}")
        except Exception as e:
            print(f"[OPTIMIZE] Failed to save prompt history: {str(e)}")
    else:
        print(f"[OPTIMIZE] Not saving to history - user: {user is not None}, error: {result.get('error')}")
    
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
