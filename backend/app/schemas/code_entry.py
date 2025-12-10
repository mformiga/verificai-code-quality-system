"""
Schemas for code entry API
"""
from datetime import datetime
from typing import Optional, Union
from pydantic import BaseModel, Field, validator
from uuid import UUID


class CodeEntryBase(BaseModel):
    """Base schema for code entry"""
    code_content: str = Field(..., min_length=1, description="The code content to save")
    title: str = Field(..., min_length=1, max_length=500, description="Title for the code entry")
    description: Optional[str] = Field(None, description="Optional description of the code")
    language: Optional[str] = Field(None, max_length=50, description="Programming language")

    @validator('code_content')
    def validate_code_content(cls, v):
        """Validate that code content is not empty or just whitespace"""
        if not v or v.strip() == '':
            raise ValueError('Code content cannot be empty')
        return v

    @validator('title')
    def validate_title(cls, v):
        """Validate that title is not empty or just whitespace"""
        if not v or v.strip() == '':
            raise ValueError('Title cannot be empty')
        return v.strip()


class CodeEntryCreate(CodeEntryBase):
    """Schema for creating a code entry"""
    lines_count: int = Field(..., ge=1, description="Number of lines in the code")
    characters_count: int = Field(..., ge=1, description="Number of characters in the code")


class CodeEntryUpdate(BaseModel):
    """Schema for updating a code entry"""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    language: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None


class CodeEntryResponse(CodeEntryBase):
    """Schema for code entry response"""
    id: Union[str, UUID]
    lines_count: int
    characters_count: int
    created_at: datetime
    updated_at: datetime
    user_id: int
    is_active: bool

    @validator('id', pre=True)
    def convert_uuid_to_str(cls, v):
        """Convert UUID to string if needed"""
        if isinstance(v, UUID):
            return str(v)
        return v

    class Config:
        from_attributes = True


class CodeEntryList(BaseModel):
    """Schema for listing code entries"""
    id: Union[str, UUID]
    title: str
    description: Optional[str] = None
    language: Optional[str] = None
    lines_count: int
    characters_count: int
    created_at: datetime
    is_active: bool = True
    code_content: str  # Schema updated for code content field - VERSION 2

    @validator('id', pre=True)
    def convert_uuid_to_str(cls, v):
        """Convert UUID to string if needed"""
        if isinstance(v, UUID):
            return str(v)
        return v

    class Config:
        from_attributes = True


class CodeEntryDeleteResponse(BaseModel):
    """Schema for delete response"""
    message: str
    success: bool


class CodeLanguageDetection(BaseModel):
    """Schema for language detection response"""
    language: str
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)


class CodeEntryStats(BaseModel):
    """Schema for code entry statistics"""
    language: str
    count: int