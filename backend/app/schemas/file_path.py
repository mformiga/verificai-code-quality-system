"""
Schema for FilePath model
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class FilePathBase(BaseModel):
    """Base schema for FilePath"""
    full_path: str = Field(..., description="Complete file path")
    file_name: str = Field(..., description="File name with extension")
    file_extension: Optional[str] = Field(None, description="File extension")
    folder_path: str = Field(..., description="Directory path")
    file_size: Optional[int] = Field(None, description="File size in bytes")
    last_modified: Optional[datetime] = Field(None, description="Last modified timestamp")
    file_metadata: Optional[dict] = Field(None, description="Additional file metadata")


class FilePathCreate(FilePathBase):
    """Schema for creating FilePath"""
    pass


class FilePathUpdate(BaseModel):
    """Schema for updating FilePath"""
    is_processed: Optional[bool] = Field(None, description="Whether file is processed")
    processing_status: Optional[str] = Field(None, description="Processing status")
    processing_error: Optional[str] = Field(None, description="Processing error message")
    file_metadata: Optional[dict] = Field(None, description="Additional file metadata")


class FilePathResponse(FilePathBase):
    """Schema for FilePath response"""
    id: int = Field(..., description="File path ID")
    file_id: str = Field(..., description="Unique file identifier")
    is_processed: bool = Field(..., description="Whether file is processed")
    processing_status: Optional[str] = Field(None, description="Processing status")
    processing_error: Optional[str] = Field(None, description="Processing error message")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    user_id: int = Field(..., description="User ID")

    class Config:
        """Pydantic configuration"""
        from_attributes = True


class FilePathBulkCreate(BaseModel):
    """Schema for bulk creating FilePath records"""
    file_paths: List[FilePathCreate] = Field(..., description="List of file paths to create")


class FilePathBulkResponse(BaseModel):
    """Schema for bulk FilePath response"""
    created_count: int = Field(..., description="Number of file paths created")
    file_paths: List[FilePathResponse] = Field(..., description="Created file paths")
    errors: List[str] = Field(default_factory=list, description="Error messages")


class FilePathListResponse(BaseModel):
    """Schema for FilePath list response"""
    file_paths: List[FilePathResponse] = Field(..., description="List of file paths")
    total_count: int = Field(..., description="Total number of file paths")
    page: int = Field(1, description="Current page")
    per_page: int = Field(20, description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")