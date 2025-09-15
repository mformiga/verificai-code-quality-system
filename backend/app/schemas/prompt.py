"""
Prompt Pydantic schemas for VerificAI Backend
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, validator

from app.models.prompt import PromptCategory, PromptStatus


class PromptBase(BaseModel):
    """Base prompt schema"""
    name: str = Field(..., min_length=1, max_length=200, description="Prompt name")
    description: Optional[str] = Field(None, description="Prompt description")
    category: PromptCategory = Field(..., description="Prompt category")
    system_prompt: str = Field(..., description="System prompt")
    user_prompt_template: str = Field(..., description="User prompt template")
    output_format_instructions: Optional[str] = Field(None, description="Output format instructions")
    temperature: float = Field(default=0.1, ge=0.0, le=2.0, description="Temperature setting")
    max_tokens: int = Field(default=4096, ge=1, le=100000, description="Maximum tokens")
    model_name: str = Field(default="gpt-4-turbo-preview", description="Model name")
    tags: Optional[List[str]] = Field(default_factory=list, description="Tags")
    is_public: bool = Field(default=False, description="Is public")
    is_featured: bool = Field(default=False, description="Is featured")
    supported_languages: Optional[List[str]] = Field(default_factory=list, description="Supported languages")
    supported_file_types: Optional[List[str]] = Field(default_factory=list, description="Supported file types")


class PromptCreate(PromptBase):
    """Prompt creation schema"""
    pass


class PromptUpdate(BaseModel):
    """Prompt update schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=200, description="Prompt name")
    description: Optional[str] = Field(None, description="Prompt description")
    category: Optional[PromptCategory] = Field(None, description="Prompt category")
    system_prompt: Optional[str] = Field(None, description="System prompt")
    user_prompt_template: Optional[str] = Field(None, description="User prompt template")
    output_format_instructions: Optional[str] = Field(None, description="Output format instructions")
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0, description="Temperature setting")
    max_tokens: Optional[int] = Field(None, ge=1, le=100000, description="Maximum tokens")
    model_name: Optional[str] = Field(None, description="Model name")
    tags: Optional[List[str]] = Field(None, description="Tags")
    is_public: Optional[bool] = Field(None, description="Is public")
    is_featured: Optional[bool] = Field(None, description="Is featured")
    supported_languages: Optional[List[str]] = Field(None, description="Supported languages")
    supported_file_types: Optional[List[str]] = Field(None, description="Supported file types")
    status: Optional[PromptStatus] = Field(None, description="Prompt status")


class PromptResponse(PromptBase):
    """Prompt response schema"""
    id: int = Field(..., description="Prompt ID")
    status: PromptStatus = Field(..., description="Prompt status")
    version: str = Field(..., description="Version")
    usage_count: int = Field(..., description="Usage count")
    success_rate: float = Field(..., description="Success rate")
    average_response_time: float = Field(..., description="Average response time")
    created_at: datetime = Field(..., description="Creation time")
    updated_at: datetime = Field(..., description="Update time")
    author_id: int = Field(..., description="Author ID")

    class Config:
        from_attributes = True


class PromptListResponse(BaseModel):
    """Prompt list response schema"""
    prompts: List[PromptResponse]
    total: int
    page: int
    per_page: int


class PromptSearchFilters(BaseModel):
    """Prompt search filters schema"""
    category: Optional[PromptCategory] = Field(None, description="Filter by category")
    status: Optional[PromptStatus] = Field(None, description="Filter by status")
    is_public: Optional[bool] = Field(None, description="Filter by public status")
    is_featured: Optional[bool] = Field(None, description="Filter by featured status")
    author_id: Optional[int] = Field(None, description="Filter by author")
    supported_language: Optional[str] = Field(None, description="Filter by supported language")
    supported_file_type: Optional[str] = Field(None, description="Filter by supported file type")
    created_after: Optional[str] = Field(None, description="Created after date")
    created_before: Optional[str] = Field(None, description="Created before date")
    search: Optional[str] = Field(None, description="Search term")


class PromptUsageStats(BaseModel):
    """Prompt usage statistics schema"""
    prompt_id: int
    total_usage: int
    successful_usage: int
    failed_usage: int
    success_rate: float
    average_response_time: float
    last_used: Optional[datetime]


class PromptCategoryStats(BaseModel):
    """Prompt category statistics schema"""
    category: PromptCategory
    total_prompts: int
    active_prompts: int
    total_usage: int
    average_success_rate: float


class PromptVersion(BaseModel):
    """Prompt version schema"""
    id: int
    name: str
    version: str
    created_at: datetime
    is_current: bool


class PromptTestRequest(BaseModel):
    """Prompt test request schema"""
    code_content: str = Field(..., description="Code content to test")
    language: str = Field(..., description="Programming language")
    file_name: Optional[str] = Field(None, description="File name")
    override_settings: Optional[dict] = Field(None, description="Override prompt settings")


class PromptTestResponse(BaseModel):
    """Prompt test response schema"""
    success: bool
    response: str
    tokens_used: Optional[int]
    processing_time: Optional[float]
    cost_estimate: Optional[float]
    error_message: Optional[str]


class PromptCloneRequest(BaseModel):
    """Prompt clone request schema"""
    new_name: str = Field(..., description="New prompt name")
    new_description: Optional[str] = Field(None, description="New description")


class PromptExportRequest(BaseModel):
    """Prompt export request schema"""
    format: str = Field(default="json", description="Export format")
    include_metadata: bool = Field(default=True, description="Include metadata")
    include_usage_stats: bool = Field(default=False, description="Include usage stats")


class PromptImportRequest(BaseModel):
    """Prompt import request schema"""
    file_content: str = Field(..., description="File content")
    format: str = Field(default="json", description="Import format")


class PromptValidationResult(BaseModel):
    """Prompt validation result schema"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    suggestions: List[str]