"""
Clerk Authentication Module
JWT validation and user extraction for Clerk auth.
"""
import jwt
import httpx
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt import PyJWKClient
from functools import lru_cache
from typing import Optional
from pydantic import BaseModel

from app.core.config import get_settings


security = HTTPBearer(auto_error=False)


class ClerkUser(BaseModel):
    """Represents an authenticated Clerk user."""
    id: str
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


@lru_cache()
def get_jwk_client() -> PyJWKClient:
    """Get cached JWK client for Clerk."""
    settings = get_settings()
    return PyJWKClient(settings.clerk_jwks_url)


async def verify_clerk_token(token: str) -> dict:
    """Verify a Clerk JWT token and return claims."""
    try:
        jwk_client = get_jwk_client()
        signing_key = jwk_client.get_signing_key_from_jwt(token)
        
        claims = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            options={"verify_aud": False}
        )
        return claims
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> ClerkUser:
    """
    FastAPI dependency to get the current authenticated user.
    Raises 401 if no valid token is provided.
    """
    if not credentials:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    claims = await verify_clerk_token(credentials.credentials)
    
    return ClerkUser(
        id=claims.get("sub"),
        email=claims.get("email"),
        first_name=claims.get("first_name"),
        last_name=claims.get("last_name")
    )


async def get_optional_user(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> Optional[ClerkUser]:
    """
    FastAPI dependency to optionally get the current user.
    Returns None for guest mode (no token).
    """
    if not credentials:
        return None
    
    try:
        claims = await verify_clerk_token(credentials.credentials)
        return ClerkUser(
            id=claims.get("sub"),
            email=claims.get("email"),
            first_name=claims.get("first_name"),
            last_name=claims.get("last_name")
        )
    except HTTPException:
        return None
