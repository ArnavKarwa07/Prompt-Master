"""
Supabase Client Module
Handles connection to Supabase for database and storage operations.
"""
from supabase import create_client, Client
from functools import lru_cache
from app.core.config import get_settings


@lru_cache()
def get_supabase_client() -> Client:
    """Get cached Supabase client instance."""
    settings = get_settings()
    return create_client(
        settings.supabase_url,
        settings.supabase_service_key
    )


class SupabaseService:
    """Service class for Supabase operations."""
    
    def __init__(self):
        self.client = get_supabase_client()
        self.settings = get_settings()
    
    # ============ User Operations ============
    async def get_user_by_id(self, user_id: str) -> dict | None:
        """Fetch user by ID."""
        result = self.client.table("users").select("*").eq("id", user_id).single().execute()
        return result.data if result.data else None
    
    async def create_user(self, user_id: str, email: str) -> dict:
        """Create a new user."""
        result = self.client.table("users").insert({
            "id": user_id,
            "email": email
        }).execute()
        return result.data[0]
    
    # ============ Project Operations ============
    async def create_project(self, user_id: str, name: str) -> dict:
        """Create a new project for a user."""
        result = self.client.table("projects").insert({
            "user_id": user_id,
            "name": name
        }).execute()
        return result.data[0]
    
    async def get_user_projects(self, user_id: str) -> list:
        """Get all projects for a user."""
        result = self.client.table("projects").select("*").eq("user_id", user_id).execute()
        return result.data or []
    
    async def get_project(self, project_id: str) -> dict | None:
        """Get a single project by ID."""
        result = self.client.table("projects").select("*").eq("id", project_id).single().execute()
        return result.data if result.data else None
    
    async def delete_project(self, project_id: str) -> bool:
        """Delete a project and its associated data."""
        # Delete prompt history first
        self.client.table("prompt_history").delete().eq("project_id", project_id).execute()
        # Delete project
        self.client.table("projects").delete().eq("id", project_id).execute()
        return True
    
    # ============ Prompt History Operations ============
    async def save_prompt_history(
        self, 
        project_id: str, 
        prompt_text: str, 
        agent_used: str, 
        score: int,
        optimized_prompt: str | None = None
    ) -> dict:
        """Save a prompt to history."""
        result = self.client.table("prompt_history").insert({
            "project_id": project_id,
            "prompt_text": prompt_text[:1000],  # Limit text storage
            "agent_used": agent_used,
            "score": score,
            "optimized_prompt": optimized_prompt[:2000] if optimized_prompt else None
        }).execute()
        return result.data[0]
    
    async def get_prompt_history(self, project_id: str, limit: int = 20) -> list:
        """Get prompt history for a project."""
        result = (
            self.client.table("prompt_history")
            .select("*")
            .eq("project_id", project_id)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return result.data or []
    
    # ============ Vector Operations ============
    async def store_vectors(
        self, 
        embeddings: list[list[float]], 
        summaries: list[str],
        metadata: list[dict]
    ) -> list:
        """Store vectors in the knowledge_vectors table."""
        records = []
        for emb, summary, meta in zip(embeddings, summaries, metadata):
            records.append({
                "embedding": emb,
                "chunk_summary": summary[:255],  # Enforce varchar limit
                "metadata": meta
            })
        
        result = self.client.table("knowledge_vectors").insert(records).execute()
        return result.data
    
    async def search_vectors(
        self, 
        query_embedding: list[float], 
        match_threshold: float = 0.7,
        match_count: int = 5
    ) -> list:
        """Search for similar vectors using cosine similarity."""
        result = self.client.rpc(
            "match_knowledge_vectors",
            {
                "query_embedding": query_embedding,
                "match_threshold": match_threshold,
                "match_count": match_count
            }
        ).execute()
        return result.data or []
    
    # ============ Storage Operations ============
    async def upload_file(self, file_path: str, file_content: bytes, user_id: str) -> str:
        """Upload file to Supabase Storage."""
        storage_path = f"{user_id}/{file_path}"
        self.client.storage.from_(self.settings.storage_bucket).upload(
            storage_path,
            file_content,
            {"content-type": "application/octet-stream"}
        )
        return storage_path
    
    async def get_file_url(self, storage_path: str) -> str:
        """Get public URL for a stored file."""
        return self.client.storage.from_(self.settings.storage_bucket).get_public_url(storage_path)
    
    async def delete_file(self, storage_path: str) -> bool:
        """Delete a file from storage."""
        self.client.storage.from_(self.settings.storage_bucket).remove([storage_path])
        return True


def get_supabase_service() -> SupabaseService:
    """Dependency injection for Supabase service."""
    return SupabaseService()
