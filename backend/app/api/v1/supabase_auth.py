"""
Supabase Authentication API Routes for AVALIA
This module provides authentication endpoints that work with Supabase
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any

from app.core.supabase import get_supabase_services
from app.dependencies.supabase import get_supabase_services_dep, get_current_user

router = APIRouter()
security = HTTPBearer()


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    username: Optional[str] = None


class ResetPasswordRequest(BaseModel):
    email: EmailStr


class UpdatePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class UpdateProfileRequest(BaseModel):
    full_name: Optional[str] = None
    bio: Optional[str] = None
    preferred_language: Optional[str] = None
    timezone: Optional[str] = None
    email_notifications: Optional[bool] = None
    email_analysis_reports: Optional[bool] = None
    email_security_alerts: Optional[bool] = None


@router.post("/auth/signup")
async def signup(
    request: SignupRequest,
    services: dict = Depends(get_supabase_services_dep)
):
    """
    Sign up a new user
    """
    try:
        auth = services["auth"]
        database = services["database"]

        # Create user in Supabase Auth
        user_data = {
            "full_name": request.full_name,
            "username": request.username
        }

        auth_result = auth.sign_up(request.email, request.password, user_data)

        if not auth_result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=auth_result.get("error", "Failed to create account")
            )

        # User profile will be created automatically via trigger
        return {
            "success": True,
            "message": "Account created successfully. Please check your email to verify your account.",
            "user_id": auth_result["user"].id
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during signup: {str(e)}"
        )


@router.post("/auth/login")
async def login(
    request: LoginRequest,
    services: dict = Depends(get_supabase_services_dep)
):
    """
    Authenticate user and return session token
    """
    try:
        auth = services["auth"]

        auth_result = auth.sign_in(request.email, request.password)

        if not auth_result["success"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # Get user profile
        database = services["database"]
        profile_result = database.select("profiles", "*", {"id": auth_result["user"].id})

        profile_data = {}
        if profile_result["success"] and profile_result["data"]:
            profile_data = profile_result["data"][0]

        return {
            "success": True,
            "message": "Login successful",
            "access_token": auth_result["session"].access_token,
            "refresh_token": auth_result["session"].refresh_token,
            "user": {
                "id": auth_result["user"].id,
                "email": auth_result["user"].email,
                "profile": profile_data
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during login: {str(e)}"
        )


@router.post("/auth/logout")
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    services: dict = Depends(get_supabase_services_dep)
):
    """
    Logout user and invalidate session
    """
    try:
        auth = services["auth"]

        auth_result = auth.sign_out(credentials.credentials)

        if not auth_result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to logout"
            )

        return {
            "success": True,
            "message": "Logout successful"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during logout: {str(e)}"
        )


@router.post("/auth/reset-password")
async def reset_password(
    request: ResetPasswordRequest,
    services: dict = Depends(get_supabase_services_dep)
):
    """
    Send password reset email
    """
    try:
        auth = services["auth"]

        auth_result = auth.reset_password(request.email)

        if not auth_result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to send reset email"
            )

        return {
            "success": True,
            "message": "Password reset email sent successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while sending reset email: {str(e)}"
        )


@router.get("/auth/me")
async def get_current_user_info(
    current_user: dict = Depends(get_current_user)
):
    """
    Get current user information
    """
    return {
        "success": True,
        "user": current_user
    }


@router.put("/auth/profile")
async def update_profile(
    request: UpdateProfileRequest,
    current_user: dict = Depends(get_current_user),
    services: dict = Depends(get_supabase_services_dep)
):
    """
    Update user profile
    """
    try:
        database = services["database"]

        # Prepare update data
        update_data = {}
        for field, value in request.dict(exclude_unset=True).items():
            update_data[field] = value

        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )

        result = database.update("profiles", update_data, {"id": current_user["auth"].id})

        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update profile"
            )

        return {
            "success": True,
            "message": "Profile updated successfully",
            "profile": result["data"][0] if result["data"] else None
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while updating profile: {str(e)}"
        )


@router.post("/auth/verify-token")
async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    services: dict = Depends(get_supabase_services_dep)
):
    """
    Verify JWT token and return user information
    """
    try:
        auth = services["auth"]

        auth_result = auth.get_user(credentials.credentials)

        if not auth_result["success"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

        # Get user profile
        database = services["database"]
        profile_result = database.select("profiles", "*", {"id": auth_result["user"].id})

        profile_data = {}
        if profile_result["success"] and profile_result["data"]:
            profile_data = profile_result["data"][0]

        return {
            "success": True,
            "user": {
                "id": auth_result["user"].id,
                "email": auth_result["user"].email,
                "profile": profile_data
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while verifying token: {str(e)}"
        )


@router.get("/auth/health")
async def auth_health_check(
    services: dict = Depends(get_supabase_services_dep)
):
    """
    Health check for authentication service
    """
    try:
        # Test basic connectivity
        database = services["database"]
        test_result = database.select("profiles", "count", limit=1)

        return {
            "status": "healthy",
            "supabase_configured": True,
            "database_connected": test_result["success"]
        }

    except Exception as e:
        return {
            "status": "unhealthy",
            "supabase_configured": False,
            "error": str(e)
        }