"""
Supabase Client Module
Handles connection to Supabase for database and storage operations.
"""
from supabase import create_client, Client
import uuid
from functools import lru_cache
from app.core.config import get_settings
import logging

logger = logging.getLogger(__name__)


@lru_cache()
def get_supabase_client() -> Client:
    """Get cached Supabase client instance."""
    settings = get_settings()
    
    # Validate that required settings are present
    if not settings.supabase_url:
        raise ValueError("SUPABASE_URL environment variable is not set")
    if not settings.supabase_service_key:
        raise ValueError("SUPABASE_SERVICE_KEY environment variable is not set")
    
    logger.info(f"Initializing Supabase client with URL: {settings.supabase_url}")
    
    return create_client(
        settings.supabase_url,
        settings.supabase_service_key
    )


class SupabaseService:
    """Service class for Supabase operations."""
    
    def __init__(self):
        self.client = get_supabase_client()
        self.settings = get_settings()
    
    def _db_user_id(self, clerk_user_id: str) -> str:
        """Map Clerk user id (string) to a stable UUID v5 for DB keys."""
        return str(uuid.uuid5(uuid.NAMESPACE_URL, f"clerk:{clerk_user_id}"))
    
    # ============ User Operations ============
    async def get_user_by_id(self, user_id: str) -> dict | None:
        """Fetch user by ID."""
        try:
            db_id = self._db_user_id(user_id)
            result = (
                self.client
                .table("users")
                .select("*")
                .eq("id", db_id)
                .limit(1)
                .execute()
            )
            data = result.data or []
            return data[0] if isinstance(data, list) and len(data) > 0 else None
        except Exception as e:
            # Treat "No rows"/406 as not found rather than an error
            msg = str(e)
            if "406" in msg or "No rows" in msg:
                return None
            logger.error(f"Error fetching user {user_id}: {msg}")
            if "Invalid API" in msg or "401" in msg:
                raise ValueError("Supabase authentication failed. Check API keys.") from e
            raise
    
    async def create_user(self, user_id: str, email: str) -> dict:
        """Create a new user."""
        try:
            db_id = self._db_user_id(user_id)
            result = (
                self.client
                .table("users")
                .insert({
                    "id": db_id,
                    "email": email
                })
                .execute()
            )
            return result.data[0]
        except Exception as e:
            logger.error(f"Error creating user {user_id}: {str(e)}")
            if "Invalid API" in str(e) or "401" in str(e):
                raise ValueError("Supabase authentication failed. Check API keys.") from e
            raise
    
    # ============ Project Operations ============
    async def create_project(self, user_id: str, name: str) -> dict:
        """Create a new project for a user."""
        try:
            db_id = self._db_user_id(user_id)
            result = (
                self.client
                .table("projects")
                .insert({
                    "user_id": db_id,
                    "name": name
                })
                .execute()
            )
            return result.data[0]
        except Exception as e:
            logger.error(f"Error creating project: {str(e)}")
            if "Invalid API" in str(e) or "401" in str(e):
                raise ValueError("Supabase authentication failed. Check API keys.") from e
            raise
    
    async def get_user_projects(self, user_id: str) -> list:
        """Get all projects for a user."""
        try:
            db_id = self._db_user_id(user_id)
            result = (
                self.client
                .table("projects")
                .select("*")
                .eq("user_id", db_id)
                .execute()
            )
            return result.data or []
        except Exception as e:
            logger.error(f"Error fetching projects for user {user_id}: {str(e)}")
            # Check if it's an API key error
            if "Invalid API" in str(e) or "401" in str(e):
                logger.error("Supabase API key validation failed. Check SUPABASE_SERVICE_KEY environment variable.")
                raise ValueError("Supabase authentication failed. Please check your API keys.") from e
            raise
    
    async def get_project(self, project_id: str) -> dict | None:
        """Get a single project by ID."""
        try:
            result = (
                self.client
                .table("projects")
                .select("*")
                .eq("id", project_id)
                .limit(1)
                .execute()
            )
            data = result.data or []
            return data[0] if isinstance(data, list) and len(data) > 0 else None
        except Exception as e:
            msg = str(e)
            if "406" in msg or "No rows" in msg:
                return None
            logger.error(f"Error fetching project {project_id}: {msg}")
            if "Invalid API" in msg or "401" in msg:
                raise ValueError("Supabase authentication failed. Check API keys.") from e
            raise
    
    async def delete_project(self, project_id: str) -> bool:
        """Delete a project and its associated data."""
        try:
            # Delete prompt history first
            self.client.table("prompt_history").delete().eq("project_id", project_id).execute()
            # Delete project
            self.client.table("projects").delete().eq("id", project_id).execute()
            return True
        except Exception as e:
            logger.error(f"Error deleting project {project_id}: {str(e)}")
            if "Invalid API" in str(e) or "401" in str(e):
                raise ValueError("Supabase authentication failed. Check API keys.") from e
            raise
    
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
        try:
            result = self.client.table("prompt_history").insert({
                "project_id": project_id,
                "prompt_text": prompt_text[:1000],  # Limit text storage
                "agent_used": agent_used,
                "score": score,
                "optimized_prompt": optimized_prompt[:2000] if optimized_prompt else None
            }).execute()
            return result.data[0]
        except Exception as e:
            logger.error(f"Error saving prompt history: {str(e)}")
            if "Invalid API" in str(e) or "401" in str(e):
                raise ValueError("Supabase authentication failed. Check API keys.") from e
            raise
    
    async def get_prompt_history(self, project_id: str, limit: int = 20) -> list:
        """Get prompt history for a project."""
        try:
            result = (
                self.client.table("prompt_history")
                .select("*")
                .eq("project_id", project_id)
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )
            return result.data or []
        except Exception as e:
            logger.error(f"Error fetching prompt history for project {project_id}: {str(e)}")
            if "Invalid API" in str(e) or "401" in str(e):
                raise ValueError("Supabase authentication failed. Check API keys.") from e
            raise

    async def get_user_prompt_history(self, user_id: str, limit: int = 10) -> list:
        """Get global prompt history across all projects for a user."""
        try:
            db_id = self._db_user_id(user_id)
            # Inner join with projects to filter by user_id
            result = (
                self.client
                .table("prompt_history")
                .select("id,prompt_text,optimized_prompt,agent_used,score,created_at,project_id,projects!inner(user_id,name)")
                .eq("projects.user_id", db_id)
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )
            return result.data or []
        except Exception as e:
            logger.error(f"Error fetching global prompt history for user {user_id}: {str(e)}")
            if "Invalid API" in str(e) or "401" in str(e):
                raise ValueError("Supabase authentication failed. Check API keys.") from e
            raise

    async def enforce_global_prompt_cap(self, user_id: str, cap: int = 10) -> int:
        """Ensure a user has at most `cap` prompt history entries across all projects."""
        try:
            db_id = self._db_user_id(user_id)
            # Fetch all IDs ordered by created_at desc, beyond cap
            result = (
                self.client
                .table("prompt_history")
                .select("id,created_at,projects!inner(user_id)")
                .eq("projects.user_id", db_id)
                .order("created_at", desc=True)
                .execute()
            )
            rows = result.data or []
            if len(rows) <= cap:
                return 0
            # Determine IDs to delete (oldest beyond cap)
            ids_to_delete = [r["id"] for r in rows[cap:]]
            if not ids_to_delete:
                return 0
            del_result = (
                self.client
                .table("prompt_history")
                .delete()
                .in_("id", ids_to_delete)
                .execute()
            )
            # Return count of deleted rows if available
            try:
                return len(del_result.data or [])
            except Exception:
                return len(ids_to_delete)
        except Exception as e:
            logger.error(f"Error enforcing global prompt cap for user {user_id}: {str(e)}")
            if "Invalid API" in str(e) or "401" in str(e):
                raise ValueError("Supabase authentication failed. Check API keys.") from e
            raise

    # ============ V2 History Operations (user_id based) ============
    async def save_prompt_history_v2(
        self, 
        user_id: str,
        prompt_text: str, 
        agent_used: str, 
        score: int,
        optimized_prompt: str | None = None,
        project_id: str | None = None,
        project_name: str | None = None
    ) -> dict:
        """Save a prompt to history with user_id (project_id optional)."""
        try:
            db_user_id = self._db_user_id(user_id)
            
            # Ensure user exists
            existing_user = await self.get_user_by_id(user_id)
            if not existing_user:
                await self.create_user(user_id, "")
            
            record = {
                "user_id": db_user_id,
                "prompt_text": prompt_text[:1000],
                "agent_used": agent_used,
                "score": score,
                "optimized_prompt": optimized_prompt[:2000] if optimized_prompt else None,
            }
            if project_id:
                record["project_id"] = project_id
                
            result = self.client.table("prompt_history").insert(record).execute()
            return result.data[0]
        except Exception as e:
            logger.error(f"Error saving prompt history v2: {str(e)}")
            if "Invalid API" in str(e) or "401" in str(e):
                raise ValueError("Supabase authentication failed. Check API keys.") from e
            raise

    async def get_user_prompt_history_v2(self, user_id: str, limit: int = 10) -> list:
        """Get prompt history for a user directly via user_id column."""
        try:
            db_id = self._db_user_id(user_id)
            # Query with optional project join to get project name
            result = (
                self.client
                .table("prompt_history")
                .select("id,prompt_text,optimized_prompt,agent_used,score,created_at,project_id,projects(name)")
                .eq("user_id", db_id)
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )
            # Flatten project name (extract from nested 'projects' object)
            data = result.data or []
            for item in data:
                if item.get("projects"):
                    item["project_name"] = item["projects"].get("name")
                else:
                    item["project_name"] = None
                # Remove the nested 'projects' key to flatten the response
                if "projects" in item:
                    del item["projects"]
            return data
        except Exception as e:
            logger.error(f"Error fetching prompt history v2 for user {user_id}: {str(e)}")
            if "Invalid API" in str(e) or "401" in str(e):
                raise ValueError("Supabase authentication failed. Check API keys.") from e
            raise

    async def enforce_global_prompt_cap_v2(self, user_id: str, cap: int = 10) -> int:
        """Ensure a user has at most `cap` prompt history entries (using user_id column)."""
        try:
            db_id = self._db_user_id(user_id)
            # Fetch all IDs ordered by created_at desc
            result = (
                self.client
                .table("prompt_history")
                .select("id,created_at")
                .eq("user_id", db_id)
                .order("created_at", desc=True)
                .execute()
            )
            rows = result.data or []
            if len(rows) <= cap:
                return 0
            # Determine IDs to delete (oldest beyond cap)
            ids_to_delete = [r["id"] for r in rows[cap:]]
            if not ids_to_delete:
                return 0
            del_result = (
                self.client
                .table("prompt_history")
                .delete()
                .in_("id", ids_to_delete)
                .execute()
            )
            print(f"[SUPABASE] Deleted {len(ids_to_delete)} old history entries for user")
            return len(ids_to_delete)
        except Exception as e:
            logger.error(f"Error enforcing global prompt cap v2: {str(e)}")
            if "Invalid API" in str(e) or "401" in str(e):
                raise ValueError("Supabase authentication failed. Check API keys.") from e
            raise
    
    # ============ Vector Operations ============
    async def store_vectors(
        self, 
        embeddings: list[list[float]], 
        summaries: list[str],
        metadata: list[dict]
    ) -> list:
        """Store vectors in the knowledge_vectors table."""
        try:
            records = []
            for emb, summary, meta in zip(embeddings, summaries, metadata):
                records.append({
                    "embedding": emb,
                    "chunk_summary": summary[:255],  # Enforce varchar limit
                    "metadata": meta
                })
            
            result = self.client.table("knowledge_vectors").insert(records).execute()
            return result.data
        except Exception as e:
            logger.error(f"Error storing vectors: {str(e)}")
            if "Invalid API" in str(e) or "401" in str(e):
                raise ValueError("Supabase authentication failed. Check API keys.") from e
            raise
    
    async def search_vectors(
        self, 
        query_embedding: list[float], 
        match_threshold: float = 0.7,
        match_count: int = 5
    ) -> list:
        """Search for similar vectors using cosine similarity."""
        try:
            result = self.client.rpc(
                "match_knowledge_vectors",
                {
                    "query_embedding": query_embedding,
                    "match_threshold": match_threshold,
                    "match_count": match_count
                }
            ).execute()
            return result.data or []
        except Exception as e:
            logger.error(f"Error searching vectors: {str(e)}")
            if "Invalid API" in str(e) or "401" in str(e):
                raise ValueError("Supabase authentication failed. Check API keys.") from e
            raise
    
    # ============ Storage Operations ============
    async def ensure_bucket_exists(self) -> bool:
        """Ensure the storage bucket exists, create if not."""
        try:
            buckets = self.client.storage.list_buckets()
            bucket_names = [b.name for b in buckets]
            
            if self.settings.storage_bucket not in bucket_names:
                print(f"[STORAGE] Creating bucket: {self.settings.storage_bucket}")
                self.client.storage.create_bucket(
                    self.settings.storage_bucket,
                    options={"public": False}
                )
                print(f"[STORAGE] Bucket created successfully")
            return True
        except Exception as e:
            print(f"[STORAGE] Error ensuring bucket exists: {str(e)}")
            return False
    
    async def upload_file(self, file_path: str, file_content: bytes, user_id: str) -> str:
        """Upload file to Supabase Storage."""
        try:
            # Ensure bucket exists
            await self.ensure_bucket_exists()
            
            storage_path = f"{self._db_user_id(user_id)}/{file_path}"
            print(f"[STORAGE] Uploading to: {storage_path}")
            
            self.client.storage.from_(self.settings.storage_bucket).upload(
                storage_path,
                file_content,
                {"content-type": "application/octet-stream", "upsert": "true"}
            )
            print(f"[STORAGE] Upload successful: {storage_path}")
            return storage_path
        except Exception as e:
            error_msg = str(e)
            print(f"[STORAGE] Error uploading file: {error_msg}")
            
            # Handle specific errors
            if "Bucket not found" in error_msg:
                raise ValueError("Storage bucket not configured. Please create the bucket in Supabase Dashboard.") from e
            if "Invalid API" in error_msg or "401" in error_msg:
                raise ValueError("Supabase authentication failed. Check API keys.") from e
            if "Duplicate" in error_msg or "already exists" in error_msg.lower():
                # File already exists, return path anyway
                return f"{self._db_user_id(user_id)}/{file_path}"
            raise
    
    async def get_file_url(self, storage_path: str) -> str:
        """Get public URL for a stored file."""
        try:
            return self.client.storage.from_(self.settings.storage_bucket).get_public_url(storage_path)
        except Exception as e:
            logger.error(f"Error getting file URL: {str(e)}")
            if "Invalid API" in str(e) or "401" in str(e):
                raise ValueError("Supabase authentication failed. Check API keys.") from e
            raise
    
    async def delete_file(self, storage_path: str) -> bool:
        """Delete a file from storage."""
        try:
            self.client.storage.from_(self.settings.storage_bucket).remove([storage_path])
            return True
        except Exception as e:
            logger.error(f"Error deleting file: {str(e)}")
            if "Invalid API" in str(e) or "401" in str(e):
                raise ValueError("Supabase authentication failed. Check API keys.") from e
            raise

    # ============ User Context Vector Operations ============
    async def store_user_context_vectors(
        self, 
        user_id: str,
        project_id: str | None,
        embeddings: list[list[float]], 
        texts: list[str],
        file_name: str,
        metadata: list[dict] | None = None
    ) -> list:
        """Store context vectors for a user/project."""
        try:
            db_user_id = self._db_user_id(user_id)
            records = []
            for i, (emb, text) in enumerate(zip(embeddings, texts)):
                record = {
                    "user_id": db_user_id,
                    "embedding": emb,
                    "content_text": text[:5000],  # Limit text size
                    "file_name": file_name,
                    "metadata": metadata[i] if metadata else {}
                }
                if project_id:
                    record["project_id"] = project_id
                records.append(record)
            
            result = self.client.table("user_context_vectors").insert(records).execute()
            print(f"[VECTORS] Stored {len(records)} context vectors for user")
            return result.data or []
        except Exception as e:
            logger.error(f"Error storing user context vectors: {str(e)}")
            if "Invalid API" in str(e) or "401" in str(e):
                raise ValueError("Supabase authentication failed. Check API keys.") from e
            raise

    async def search_user_context(
        self,
        user_id: str,
        query_embedding: list[float],
        project_id: str | None = None,
        match_threshold: float = 0.7,
        match_count: int = 5
    ) -> list:
        """Search context vectors for a user (optionally filtered by project)."""
        try:
            db_user_id = self._db_user_id(user_id)
            # Use raw SQL for vector similarity search with user filter
            # Note: This requires the match_user_context_vectors function to be created
            params = {
                "query_embedding": query_embedding,
                "p_user_id": db_user_id,
                "match_threshold": match_threshold,
                "match_count": match_count
            }
            if project_id:
                params["p_project_id"] = project_id
            
            result = self.client.rpc(
                "match_user_context_vectors",
                params
            ).execute()
            return result.data or []
        except Exception as e:
            # If function doesn't exist, fall back to basic query
            logger.warning(f"Vector search function not available: {str(e)}")
            return []

    async def delete_user_context_vectors(self, user_id: str, project_id: str | None = None) -> int:
        """Delete context vectors for a user (optionally for specific project)."""
        try:
            db_user_id = self._db_user_id(user_id)
            query = self.client.table("user_context_vectors").delete().eq("user_id", db_user_id)
            if project_id:
                query = query.eq("project_id", project_id)
            result = query.execute()
            return len(result.data or [])
        except Exception as e:
            logger.error(f"Error deleting user context vectors: {str(e)}")
            if "Invalid API" in str(e) or "401" in str(e):
                raise ValueError("Supabase authentication failed. Check API keys.") from e
            raise


def get_supabase_service() -> SupabaseService:
    """Dependency injection for Supabase service."""
    return SupabaseService()
