"""
Project Routes
API endpoints for project management (authenticated users).
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from typing import Optional

from app.api.models import (
    CreateProjectRequest,
    ProjectResponse,
    ProjectListResponse,
    PromptHistoryResponse,
    PromptHistoryItem
)
from app.core.auth import get_current_user, ClerkUser
from app.core.supabase_client import get_supabase_service, SupabaseService


router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ProjectResponse)
async def create_project(
    request: CreateProjectRequest,
    user: ClerkUser = Depends(get_current_user),
    supabase: SupabaseService = Depends(get_supabase_service)
):
    """Create a new project."""
    # Ensure user exists in database
    existing_user = await supabase.get_user_by_id(user.id)
    if not existing_user:
        await supabase.create_user(user.id, user.email or "")
    
    project = await supabase.create_project(user.id, request.name)
    
    return ProjectResponse(
        id=project["id"],
        name=project["name"],
        created_at=project.get("created_at")
    )


@router.get("", response_model=ProjectListResponse)
async def list_projects(
    user: ClerkUser = Depends(get_current_user),
    supabase: SupabaseService = Depends(get_supabase_service)
):
    """List all projects for the current user."""
    projects = await supabase.get_user_projects(user.id)
    
    return ProjectListResponse(
        projects=[
            ProjectResponse(
                id=p["id"],
                name=p["name"],
                created_at=p.get("created_at")
            )
            for p in projects
        ]
    )


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    user: ClerkUser = Depends(get_current_user),
    supabase: SupabaseService = Depends(get_supabase_service)
):
    """Get a specific project."""
    project = await supabase.get_project(project_id)
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if project["user_id"] != user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return ProjectResponse(
        id=project["id"],
        name=project["name"],
        created_at=project.get("created_at")
    )


@router.delete("/{project_id}")
async def delete_project(
    project_id: str,
    user: ClerkUser = Depends(get_current_user),
    supabase: SupabaseService = Depends(get_supabase_service)
):
    """Delete a project and all associated data."""
    project = await supabase.get_project(project_id)
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if project["user_id"] != user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    await supabase.delete_project(project_id)
    
    return {"message": "Project deleted successfully"}


@router.get("/{project_id}/history", response_model=PromptHistoryResponse)
async def get_prompt_history(
    project_id: str,
    limit: int = 20,
    user: ClerkUser = Depends(get_current_user),
    supabase: SupabaseService = Depends(get_supabase_service)
):
    """Get prompt history for a project."""
    project = await supabase.get_project(project_id)
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if project["user_id"] != user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    history = await supabase.get_prompt_history(project_id, limit)
    
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


@router.post("/{project_id}/upload")
async def upload_context_file(
    project_id: str,
    file: UploadFile = File(...),
    user: ClerkUser = Depends(get_current_user),
    supabase: SupabaseService = Depends(get_supabase_service)
):
    """
    Upload a context file for a project.
    File is stored in Supabase Storage, then processed for embeddings.
    """
    # Verify project access
    project = await supabase.get_project(project_id)
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if project["user_id"] != user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Read file content
    content = await file.read()
    
    # Check file size (limit to 5MB)
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size exceeds 5MB limit")
    
    # Upload to storage
    storage_path = await supabase.upload_file(
        file_path=f"{project_id}/{file.filename}",
        file_content=content,
        user_id=user.id
    )
    
    # TODO: Extract text and create embeddings
    # This would be done asynchronously in production
    
    return {
        "message": "File uploaded successfully",
        "storage_path": storage_path,
        "filename": file.filename
    }
