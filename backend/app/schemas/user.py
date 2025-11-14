"""
User Pydantic schemas for VerificAI Backend
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, validator, SecretStr
from enum import Enum

from app.models.user import UserRole


class UserRoleSchema(str, Enum):
    """User role schema"""
    ADMIN = "ADMIN"
    QA_ENGINEER = "QA_ENGINEER"
    DEVELOPER = "DEVELOPER"
    VIEWER = "VIEWER"


class UserBase(BaseModel):
    """Base user schema"""
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    email: EmailStr = Field(..., description="Email address")
    full_name: Optional[str] = Field(None, max_length=100, description="Full name")
    role: UserRoleSchema = Field(default=UserRoleSchema.QA_ENGINEER, description="User role")
    bio: Optional[str] = Field(None, max_length=500, description="User bio")
    preferred_language: str = Field(default="en", description="Preferred language")
    timezone: str = Field(default="UTC", description="User timezone")
    email_notifications: bool = Field(default=True, description="Email notifications enabled")
    email_analysis_reports: bool = Field(default=True, description="Analysis report emails")
    email_security_alerts: bool = Field(default=True, description="Security alert emails")


class UserCreate(UserBase):
    """User creation schema"""
    password: str = Field(..., min_length=8, description="Password")
    confirm_password: str = Field(..., min_length=8, description="Confirm password")

    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v

    @validator('password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        if not any(c in '!@#$%^&*(),.?":{}|<>' for c in v):
            raise ValueError('Password must contain at least one special character')
        return v


class UserUpdate(BaseModel):
    """User update schema"""
    full_name: Optional[str] = Field(None, max_length=100, description="Full name")
    bio: Optional[str] = Field(None, max_length=500, description="User bio")
    preferred_language: Optional[str] = Field(None, description="Preferred language")
    timezone: Optional[str] = Field(None, description="User timezone")
    email_notifications: Optional[bool] = Field(None, description="Email notifications enabled")
    email_analysis_reports: Optional[bool] = Field(None, description="Analysis report emails")
    email_security_alerts: Optional[bool] = Field(None, description="Security alert emails")


class UserPasswordUpdate(BaseModel):
    """User password update schema"""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")
    confirm_password: str = Field(..., min_length=8, description="Confirm new password")

    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v

    @validator('new_password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        if not any(c in '!@#$%^&*(),.?":{}|<>' for c in v):
            raise ValueError('Password must contain at least one special character')
        return v


class UserLogin(BaseModel):
    """User login schema"""
    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="Password")


class UserResponse(UserBase):
    """User response schema"""
    id: int = Field(..., description="User ID")
    is_active: bool = Field(..., description="Is user active")
    is_verified: bool = Field(..., description="Is user verified")
    is_admin: bool = Field(..., description="Is user admin")
    avatar_url: Optional[str] = Field(None, description="Avatar URL")
    last_login: Optional[datetime] = Field(None, description="Last login time")
    created_at: datetime = Field(..., description="Creation time")
    updated_at: datetime = Field(..., description="Update time")

    class Config:
        from_attributes = True


class UserProfile(UserResponse):
    """User profile schema"""
    total_analyses: int = Field(default=0, description="Total analyses created")
    total_prompts: int = Field(default=0, description="Total prompts created")
    api_key_created: bool = Field(default=False, description="API key created")
    has_password: bool = Field(default=True, description="Has password set")


class UserListResponse(BaseModel):
    """User list response schema"""
    users: List[UserResponse]
    total: int
    page: int
    per_page: int


class UserStats(BaseModel):
    """User statistics schema"""
    total_users: int = Field(..., description="Total users")
    active_users: int = Field(..., description="Active users")
    new_users_today: int = Field(..., description="New users today")
    new_users_week: int = Field(..., description="New users this week")
    new_users_month: int = Field(..., description="New users this month")
    users_by_role: dict = Field(..., description="Users by role")


class UserActivity(BaseModel):
    """User activity schema"""
    user_id: int
    username: str
    activity_type: str
    description: str
    timestamp: datetime
    details: Optional[dict] = None


class APIKeyCreate(BaseModel):
    """API key creation schema"""
    name: str = Field(..., description="API key name")
    expires_in_days: Optional[int] = Field(None, ge=1, le=365, description="Expiration in days")


class APIKeyResponse(BaseModel):
    """API key response schema"""
    id: int
    name: str
    api_key: str
    created_at: datetime
    expires_at: Optional[datetime]
    last_used: Optional[datetime]
    is_active: bool

    class Config:
        from_attributes = True


class UserPreferences(BaseModel):
    """User preferences schema"""
    language: str = Field(default="en", description="Preferred language")
    timezone: str = Field(default="UTC", description="User timezone")
    theme: str = Field(default="light", description="UI theme")
    date_format: str = Field(default="YYYY-MM-DD", description="Date format")
    email_notifications: bool = Field(default=True, description="Email notifications")
    analysis_reports: bool = Field(default=True, description="Analysis report emails")
    security_alerts: bool = Field(default=True, description="Security alert emails")


class PasswordResetRequest(BaseModel):
    """Password reset request schema"""
    email: EmailStr = Field(..., description="Email address")


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation schema"""
    token: str = Field(..., description="Reset token")
    new_password: str = Field(..., min_length=8, description="New password")
    confirm_password: str = Field(..., min_length=8, description="Confirm new password")

    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v

    @validator('new_password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        if not any(c in '!@#$%^&*(),.?":{}|<>' for c in v):
            raise ValueError('Password must contain at least one special character')
        return v


class EmailVerificationRequest(BaseModel):
    """Email verification request schema"""
    email: EmailStr = Field(..., description="Email address")


class EmailVerificationConfirm(BaseModel):
    """Email verification confirmation schema"""
    token: str = Field(..., description="Verification token")


class UserSearchFilters(BaseModel):
    """User search filters schema"""
    role: Optional[UserRoleSchema] = Field(None, description="Filter by role")
    is_active: Optional[bool] = Field(None, description="Filter by active status")
    is_verified: Optional[bool] = Field(None, description="Filter by verified status")
    created_after: Optional[str] = Field(None, description="Created after date")
    created_before: Optional[str] = Field(None, description="Created before date")
    search: Optional[str] = Field(None, description="Search term")