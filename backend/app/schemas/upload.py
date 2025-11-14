"""
File upload schemas for VerificAI Backend
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum


class FileStatus(str, Enum):
    """File upload status enumeration"""
    UPLOADING = "uploading"
    COMPLETED = "completed"
    ERROR = "error"
    DELETED = "deleted"


class ProcessingStatus(str, Enum):
    """File processing status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"


class FileUploadRequest(BaseModel):
    """Request schema for file upload"""
    file_id: str = Field(..., description="Unique file identifier")
    original_name: str = Field(..., description="Original file name")
    relative_path: Optional[str] = Field(None, description="Original relative path if from folder")


class FileUploadResponse(BaseModel):
    """Response schema for file upload"""
    file_id: str
    original_name: str
    file_path: str
    file_size: int
    mime_type: str
    status: FileStatus
    upload_progress: int
    message: str
    upload_date: datetime

    class Config:
        from_attributes = True


class FileListResponse(BaseModel):
    """Response schema for file list"""
    files: List[FileUploadResponse]
    total_count: int
    total_size: int


class FileUpdateRequest(BaseModel):
    """Request schema for updating file metadata"""
    status: Optional[FileStatus] = None
    upload_progress: Optional[int] = Field(None, ge=0, le=100)
    error_message: Optional[str] = None
    is_processed: Optional[bool] = None
    processing_status: Optional[ProcessingStatus] = None
    processing_error: Optional[str] = None
    language_detected: Optional[str] = None
    line_count: Optional[int] = Field(None, ge=0)
    complexity_score: Optional[str] = None
    metadata: Optional[dict] = None
    tags: Optional[List[str]] = None
    is_public: Optional[bool] = None
    access_level: Optional[str] = Field(None, pattern=r"^(private|team|public)$")


class FileAnalysisRequest(BaseModel):
    """Request schema for file analysis"""
    file_ids: List[str] = Field(..., description="List of file IDs to analyze")
    analysis_type: str = Field(..., description="Type of analysis to perform")


class FileAnalysisResponse(BaseModel):
    """Response schema for file analysis"""
    analysis_id: str
    file_ids: List[str]
    analysis_type: str
    status: str
    message: str
    created_at: datetime


class FileDeleteRequest(BaseModel):
    """Request schema for file deletion"""
    file_ids: List[str] = Field(..., description="List of file IDs to delete")


class FileDeleteResponse(BaseModel):
    """Response schema for file deletion"""
    deleted_files: List[str]
    failed_files: List[str]
    message: str


class FileStatsResponse(BaseModel):
    """Response schema for file statistics"""
    total_files: int
    total_size: int
    status_counts: dict
    file_type_counts: dict
    user_counts: dict
    recent_uploads: List[dict]


class ValidationError(BaseModel):
    """Validation error response"""
    field: str
    message: str


class UploadValidationResponse(BaseModel):
    """Upload validation response"""
    is_valid: bool
    errors: List[ValidationError]
    warnings: List[str]
    max_file_size: int
    allowed_extensions: List[str]