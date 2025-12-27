"""
History Routes
API endpoints for prompt history (authenticated users).
"""
from fastapi import APIRouter, Depends, HTTPException
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
    user: ClerkUser = Depends(get_current_user),
    supabase: SupabaseService = Depends(get_supabase_service)
):
    """
    Get prompt history for the current user across all projects.
    
    Returns the most recent prompts optimized by this user, ordered by date.
    """
    try:
        history = await supabase.get_user_prompt_history(user.id, limit)

        return PromptHistoryResponse(
            history=[
                PromptHistoryItem(
                    id=h["id"],
                    prompt_text=h["prompt_text"],
                    agent_used=h["agent_used"],
                    score=h["score"],
                    optimized_prompt=h.get("optimized_prompt"),
                    created_at=h.get("created_at")
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
