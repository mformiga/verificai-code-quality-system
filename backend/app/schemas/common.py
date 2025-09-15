"""
Common Pydantic schemas for VerificAI Backend
"""

from typing import Generic, TypeVar, Optional, List, Any
from pydantic import BaseModel, Field, validator
from enum import Enum

T = TypeVar('T')


class PaginationParams(BaseModel):
    """Pagination parameters"""
    skip: int = Field(default=0, ge=0, description="Number of items to skip")
    limit: int = Field(default=100, ge=1, le=1000, description="Number of items to return")
    sort_by: Optional[str] = Field(default=None, description="Field to sort by")
    sort_order: Optional[str] = Field(default="desc", description="Sort order (asc/desc)")
    search: Optional[str] = Field(default=None, description="Search term")

    @validator('sort_order')
    def validate_sort_order(cls, v):
        if v not in ['asc', 'desc']:
            return 'desc'
        return v


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response"""
    items: List[T]
    total: int = Field(..., description="Total number of items")
    skip: int = Field(..., description="Number of items skipped")
    limit: int = Field(..., description="Number of items returned")
    pages: int = Field(..., description="Total number of pages")
    current_page: int = Field(..., description="Current page number")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_prev: bool = Field(..., description="Whether there is a previous page")


class BaseResponse(BaseModel):
    """Base response schema"""
    success: bool = Field(default=True, description="Whether the request was successful")
    message: Optional[str] = Field(default=None, description="Response message")


class ErrorResponse(BaseModel):
    """Error response schema"""
    success: bool = Field(default=False, description="Whether the request was successful")
    error_code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    detail: Optional[Any] = Field(default=None, description="Error details")


class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")
    database: Optional[str] = Field(default=None, description="Database status")
    redis: Optional[str] = Field(default=None, description="Redis status")
    timestamp: Optional[str] = Field(default=None, description="Check timestamp")


class ReadyCheckResponse(BaseModel):
    """Readiness check response"""
    status: str = Field(..., description="Service readiness status")
    service: str = Field(..., description="Service name")
    dependencies: dict = Field(default_factory=dict, description="Dependency statuses")


class FileUploadResponse(BaseModel):
    """File upload response"""
    success: bool = Field(..., description="Whether upload was successful")
    filename: str = Field(..., description="Uploaded filename")
    file_size: int = Field(..., description="File size in bytes")
    file_path: str = Field(..., description="File path")
    content_type: str = Field(..., description="File content type")


class BatchOperationResponse(BaseModel):
    """Batch operation response"""
    success_count: int = Field(..., description="Number of successful operations")
    failed_count: int = Field(..., description="Number of failed operations")
    total_count: int = Field(..., description="Total number of operations")
    errors: List[dict] = Field(default_factory=list, description="List of errors")


class FilterParams(BaseModel):
    """Generic filter parameters"""
    category: Optional[str] = Field(default=None, description="Category filter")
    status: Optional[str] = Field(default=None, description="Status filter")
    created_after: Optional[str] = Field(default=None, description="Created after date")
    created_before: Optional[str] = Field(default=None, description="Created before date")
    author_id: Optional[int] = Field(default=None, description="Author ID filter")


class DateRangeFilter(BaseModel):
    """Date range filter"""
    start_date: Optional[str] = Field(default=None, description="Start date (YYYY-MM-DD)")
    end_date: Optional[str] = Field(default=None, description="End date (YYYY-MM-DD)")

    @validator('start_date', 'end_date')
    def validate_date_format(cls, v):
        if v is None:
            return v
        from datetime import datetime
        try:
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            raise ValueError('Date must be in YYYY-MM-DD format')


class SearchParams(BaseModel):
    """Search parameters"""
    query: Optional[str] = Field(default=None, description="Search query")
    fields: Optional[List[str]] = Field(default=None, description="Fields to search in")
    exact_match: bool = Field(default=False, description="Whether to use exact match")
    case_sensitive: bool = Field(default=False, description="Whether search is case sensitive")


class ExportParams(BaseModel):
    """Export parameters"""
    format: str = Field(default="json", description="Export format (json, csv, xml)")
    include_metadata: bool = Field(default=True, description="Whether to include metadata")
    fields: Optional[List[str]] = Field(default=None, description="Fields to include")
    filter_params: Optional[dict] = Field(default=None, description="Filter parameters")


class NotificationPreferences(BaseModel):
    """User notification preferences"""
    email_notifications: bool = Field(default=True, description="Email notifications enabled")
    email_analysis_reports: bool = Field(default=True, description="Analysis report emails")
    email_security_alerts: bool = Field(default=True, description="Security alert emails")
    push_notifications: bool = Field(default=False, description="Push notifications enabled")
    webhook_url: Optional[str] = Field(default=None, description="Webhook URL for notifications")


class UserPreferences(BaseModel):
    """User preferences"""
    language: str = Field(default="en", description="Preferred language")
    timezone: str = Field(default="UTC", description="User timezone")
    theme: str = Field(default="light", description="UI theme")
    date_format: str = Field(default="YYYY-MM-DD", description="Date format")
    notifications: NotificationPreferences = Field(default_factory=NotificationPreferences)


class APIKeyResponse(BaseModel):
    """API key response"""
    api_key: str = Field(..., description="Generated API key")
    api_key_hash: str = Field(..., description="Hashed API key for storage")
    created_at: str = Field(..., description="Creation timestamp")
    expires_at: Optional[str] = Field(default=None, description="Expiration timestamp")


class RateLimitInfo(BaseModel):
    """Rate limit information"""
    requests_per_minute: int = Field(..., description="Requests allowed per minute")
    requests_remaining: int = Field(..., description="Requests remaining in current window")
    reset_time: str = Field(..., description="Time when rate limit resets")


class SystemInfo(BaseModel):
    """System information"""
    version: str = Field(..., description="Application version")
    environment: str = Field(..., description="Environment (development/production)")
    python_version: str = Field(..., description="Python version")
    database_version: Optional[str] = Field(default=None, description="Database version")
    redis_version: Optional[str] = Field(default=None, description="Redis version")
    uptime: str = Field(..., description="System uptime")