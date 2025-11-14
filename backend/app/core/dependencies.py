"""
Dependency injection utilities for VerificAI Backend
"""

from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import redis.asyncio as redis

from app.core.database import get_db, get_redis
from app.core.security import verify_token
from app.core.exceptions import InvalidTokenError, AuthenticationError
from app.models.user import User

# Security schemes
security = HTTPBearer()


async def get_current_user(
    db: Session = Depends(get_db),
    token: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """Get current authenticated user"""
    try:
        # Verify token
        username = verify_token(token.credentials)
        if username is None:
            raise InvalidTokenError()

        # Get user from database
        user = db.query(User).filter(User.username == username).first()
        if user is None:
            raise AuthenticationError("User not found")

        if not user.is_active:
            raise AuthenticationError("User account is inactive")

        return user

    except Exception as e:
        if isinstance(e, (InvalidTokenError, AuthenticationError)):
            raise e
        raise AuthenticationError(f"Authentication failed: {str(e)}")


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


async def get_optional_user(
    db: Session = Depends(get_db),
    token: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[User]:
    """Get optional current user (for endpoints that work with or without auth)"""
    if token is None:
        return None

    try:
        return await get_current_user(db, token)
    except Exception:
        return None


async def get_redis_client() -> redis.Redis:
    """Get Redis client"""
    return await get_redis()


class CommonQueryParams:
    """Common query parameters for pagination and filtering"""

    def __init__(
        self,
        skip: int = 0,
        limit: int = 100,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = "desc",
        search: Optional[str] = None
    ):
        self.skip = skip
        self.limit = min(limit, 1000)  # Max 1000 items per page
        self.sort_by = sort_by
        self.sort_order = sort_order.lower() if sort_order else "desc"
        self.search = search

        # Validate sort order
        if self.sort_order not in ["asc", "desc"]:
            self.sort_order = "desc"


def get_pagination_params(
    skip: int = 0,
    limit: int = 100
) -> tuple[int, int]:
    """Get pagination parameters"""
    skip = max(0, skip)
    limit = min(max(1, limit), 1000)  # Between 1 and 1000
    return skip, limit


def verify_admin_permission(current_user: User = Depends(get_current_user)) -> User:
    """Verify user has admin permissions"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin permissions required"
        )
    return current_user


def verify_api_key_permission(
    api_key: Optional[str] = None,
    current_user: Optional[User] = Depends(get_optional_user)
) -> tuple[bool, Optional[User]]:
    """Verify API key or user authentication"""
    # If user is authenticated via token, allow access
    if current_user:
        return True, current_user

    # TODO: Implement API key validation
    # For now, deny access if no valid authentication
    return False, None


class RateLimitDependency:
    """Rate limiting dependency"""

    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute

    async def __call__(self, request):
        # TODO: Implement Redis-based rate limiting
        # For now, this is a placeholder
        pass


# Common dependencies
common_query_params = CommonQueryParams
rate_limit = RateLimitDependency