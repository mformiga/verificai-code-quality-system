"""
Supabase dependencies for FastAPI
This module provides dependency functions for Supabase integration
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.supabase import get_supabase_client, get_supabase_services, supabase_config

# HTTP Bearer token scheme
security = HTTPBearer(auto_error=False)


async def get_supabase_client_dep(service_role: bool = False):
    """
    FastAPI dependency to get Supabase client

    Args:
        service_role: Whether to use service role key (admin operations)

    Returns:
        Supabase client instance
    """
    client = get_supabase_client(service_role)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Supabase not configured"
        )
    return client


async def get_supabase_services_dep(service_role: bool = False):
    """
    FastAPI dependency to get Supabase services

    Args:
        service_role: Whether to use service role key (admin operations)

    Returns:
        Dictionary with Supabase service instances
    """
    services = get_supabase_services(service_role)
    if not services:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Supabase not configured"
        )
    return services


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    services: dict = Depends(get_supabase_services_dep)
):
    """
    FastAPI dependency to get current authenticated user

    Args:
        credentials: Bearer token credentials
        services: Supabase services

    Returns:
        User information
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        # Verify JWT token and get user
        auth_result = services["auth"].get_user(credentials.credentials)

        if not auth_result["success"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user = auth_result["user"]

        # Get user profile
        profile_result = services["database"].select("profiles", "*", {"id": user.id})

        if not profile_result["success"] or not profile_result["data"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )

        profile = profile_result["data"][0]

        # Check if user is active
        if not profile.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is deactivated"
            )

        return {
            "auth": user,
            "profile": profile
        }

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_active_user(current_user: dict = Depends(get_current_user)):
    """
    FastAPI dependency to get current active user

    Args:
        current_user: Current authenticated user

    Returns:
        Active user information
    """
    return current_user


async def get_current_admin_user(current_user: dict = Depends(get_current_active_user)):
    """
    FastAPI dependency to get current admin user

    Args:
        current_user: Current authenticated user

    Returns:
        Admin user information
    """
    if not current_user["profile"].get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


async def get_supabase_user_from_token(token: str):
    """
    Get Supabase user from JWT token

    Args:
        token: JWT token

    Returns:
        User information
    """
    services = get_supabase_services()
    if not services:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Supabase not configured"
        )

    auth_result = services["auth"].get_user(token)

    if not auth_result["success"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    return auth_result["user"]


def require_permissions(required_permissions: list):
    """
    Create a dependency that requires specific permissions

    Args:
        required_permissions: List of required permissions

    Returns:
        Dependency function
    """
    async def permission_dependency(current_user: dict = Depends(get_current_active_user)):
        user_role = current_user["profile"].get("role", "VIEWER")
        is_admin = current_user["profile"].get("is_admin", False)

        # Admins have all permissions
        if is_admin:
            return current_user

        # Define role permissions
        role_permissions = {
            "ADMIN": ["*"],
            "QA_ENGINEER": [
                "create_analysis", "view_analysis", "edit_prompt",
                "create_prompt", "view_reports", "upload_files"
            ],
            "DEVELOPER": [
                "create_analysis", "view_analysis", "view_prompt", "upload_files"
            ],
            "VIEWER": ["view_analysis", "view_prompt", "view_reports"]
        }

        user_permissions = role_permissions.get(user_role, [])

        # Check if user has required permissions
        for permission in required_permissions:
            if "*" not in user_permissions and permission not in user_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission '{permission}' required"
                )

        return current_user

    return permission_dependency


# Permission dependency factories
require_admin = Depends(get_current_admin_user)
require_active_user = Depends(get_current_active_user)

require_analysis_permission = require_permissions(["create_analysis", "view_analysis"])
require_prompt_permission = require_permissions(["create_prompt", "edit_prompt"])
require_file_upload_permission = require_permissions(["upload_files"])
require_report_permission = require_permissions(["view_reports"])