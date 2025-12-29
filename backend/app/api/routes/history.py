"""
History Routes
API endpoints for prompt history (authenticated users).
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
import logging

from app.api.models import (
    PromptHistoryResponse,
    PromptHistoryItem
)
from app.core.auth import get_current_user, ClerkUser
from app.core.supabase_client import get_supabase_service, SupabaseService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/history", tags=["history"])


@router.get("", response_model=PromptHistoryResponse)
async def get_user_history(
    limit: int = 10,
    project_id: Optional[str] = None,
    user: ClerkUser = Depends(get_current_user),
    supabase: SupabaseService = Depends(get_supabase_service)
):
    """
    Get prompt history for the current user.
    
    Args:
        limit: Maximum number of history items to return
        project_id: Optional project ID to filter by. If not provided, returns global history.
    
    Returns the most recent prompts optimized by this user, ordered by date.
    Includes project name if the prompt was associated with a project.
    """
    try:
        scope = f"project {project_id}" if project_id else "global"
        print(f"[HISTORY] Fetching {scope} history for user {user.id} with limit {limit}")
        # Try v2 method first (direct user_id), fall back to v1 (join via projects)
        try:
            history = await supabase.get_user_prompt_history_v2(user.id, limit, project_id)
        except Exception as e:
            # If user_id column doesn't exist, fall back to v1 method
            if "user_id does not exist" in str(e):
                print(f"[HISTORY] Falling back to v1 history method (join via projects)")
                raw_history = await supabase.get_user_prompt_history(user.id, limit)
                # Flatten v1 response format
                history = []
                for h in raw_history:
                    # Skip if project_id filter is set and doesn't match
                    if project_id and h.get("project_id") != project_id:
                        continue
                    item = {
                        "id": h["id"],
                        "prompt_text": h["prompt_text"],
                        "optimized_prompt": h.get("optimized_prompt"),
                        "agent_used": h["agent_used"],
                        "score": h["score"],
                        "created_at": h.get("created_at"),
                        "project_name": h.get("projects", {}).get("name") if h.get("projects") else None
                    }
                    history.append(item)
            else:
                raise
        print(f"[HISTORY] Found {len(history)} history items for user {user.id}")

        return PromptHistoryResponse(
            history=[
                PromptHistoryItem(
                    id=h["id"],
                    prompt_text=h["prompt_text"],
                    agent_used=h["agent_used"],
                    score=h["score"],
                    optimized_prompt=h.get("optimized_prompt"),
                    created_at=h.get("created_at"),
                    project_name=h.get("project_name")
                )
                for h in history
            ]
        )
    except ValueError as e:
        logger.error(f"Supabase configuration error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Database configuration error. Please check server logs."
        )
    except Exception as e:
        logger.error(f"Error getting prompt history for user {user.id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve prompt history"
        )
