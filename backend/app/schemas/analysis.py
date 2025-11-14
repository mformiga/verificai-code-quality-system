"""
Analysis Pydantic schemas for VerificAI Backend
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator

from app.models.analysis import AnalysisStatus


class AnalysisBase(BaseModel):
    """Base analysis schema"""
    name: str = Field(..., min_length=1, max_length=200, description="Analysis name")
    description: Optional[str] = Field(None, description="Analysis description")
    repository_url: Optional[str] = Field(None, description="Repository URL")
    file_paths: Optional[List[str]] = Field(default_factory=list, description="File paths")
    code_content: Optional[str] = Field(None, description="Raw code content")
    language: Optional[str] = Field(None, description="Programming language")
    configuration: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Analysis configuration")


class AnalysisCreate(AnalysisBase):
    """Analysis creation schema"""
    prompt_id: int = Field(..., description="Prompt ID to use")


class AnalysisUpdate(BaseModel):
    """Analysis update schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=200, description="Analysis name")
    description: Optional[str] = Field(None, description="Analysis description")
    configuration: Optional[Dict[str, Any]] = Field(None, description="Analysis configuration")


class AnalysisResponse(AnalysisBase):
    """Analysis response schema"""
    id: int = Field(..., description="Analysis ID")
    status: AnalysisStatus = Field(..., description="Analysis status")
    user_id: int = Field(..., description="User ID")
    prompt_id: int = Field(..., description="Prompt ID")
    started_at: Optional[datetime] = Field(None, description="Start time")
    completed_at: Optional[datetime] = Field(None, description="Completion time")
    error_message: Optional[str] = Field(None, description="Error message")
    progress_percentage: int = Field(..., description="Progress percentage")
    total_files: int = Field(..., description="Total files")
    total_lines: int = Field(..., description="Total lines")
    file_size_bytes: int = Field(..., description="File size in bytes")
    total_issues: int = Field(..., description="Total issues")
    critical_issues: int = Field(..., description="Critical issues")
    warning_issues: int = Field(..., description="Warning issues")
    info_issues: int = Field(..., description="Info issues")
    overall_score: Optional[int] = Field(None, description="Overall score")
    security_score: Optional[int] = Field(None, description="Security score")
    performance_score: Optional[int] = Field(None, description="Performance score")
    maintainability_score: Optional[int] = Field(None, description="Maintainability score")
    model_used: Optional[str] = Field(None, description="Model used")
    tokens_used: Optional[int] = Field(None, description="Tokens used")
    processing_time: Optional[str] = Field(None, description="Processing time")
    estimated_cost: Optional[str] = Field(None, description="Estimated cost")
    actual_cost: Optional[str] = Field(None, description="Actual cost")
    created_at: datetime = Field(..., description="Creation time")
    updated_at: datetime = Field(..., description="Update time")

    class Config:
        from_attributes = True


class AnalysisListResponse(BaseModel):
    """Analysis list response schema"""
    analyses: List[AnalysisResponse]
    total: int
    page: int
    per_page: int


class AnalysisResultResponse(BaseModel):
    """Analysis result response schema"""
    id: int = Field(..., description="Result ID")
    analysis_id: int = Field(..., description="Analysis ID")
    summary: str = Field(..., description="Analysis summary")
    detailed_findings: Optional[str] = Field(None, description="Detailed findings")
    recommendations: Optional[str] = Field(None, description="Recommendations")
    score: Optional[int] = Field(None, description="Quality score")
    confidence: Optional[float] = Field(None, description="Confidence score")
    issues: List[Dict[str, Any]] = Field(default_factory=list, description="Issues found")
    metrics: Dict[str, Any] = Field(default_factory=dict, description="Metrics")
    code_snippets: List[Dict[str, Any]] = Field(default_factory=list, description="Code snippets")
    file_analysis: Dict[str, Any] = Field(default_factory=dict, description="File analysis")
    model_used: Optional[str] = Field(None, description="Model used")
    tokens_used: Optional[int] = Field(None, description="Tokens used")
    processing_time: Optional[str] = Field(None, description="Processing time")
    quality_score: Optional[int] = Field(None, description="Quality score")
    security_score: Optional[int] = Field(None, description="Security score")
    performance_score: Optional[int] = Field(None, description="Performance score")
    maintainability_score: Optional[int] = Field(None, description="Maintainability score")
    created_at: datetime = Field(..., description="Creation time")
    updated_at: datetime = Field(..., description="Update time")

    class Config:
        from_attributes = True


class AnalysisSearchFilters(BaseModel):
    """Analysis search filters schema"""
    status: Optional[AnalysisStatus] = Field(None, description="Filter by status")
    user_id: Optional[int] = Field(None, description="Filter by user")
    prompt_id: Optional[int] = Field(None, description="Filter by prompt")
    language: Optional[str] = Field(None, description="Filter by language")
    min_score: Optional[int] = Field(None, ge=0, le=100, description="Filter by minimum score")
    max_score: Optional[int] = Field(None, ge=0, le=100, description="Filter by maximum score")
    created_after: Optional[str] = Field(None, description="Created after date")
    created_before: Optional[str] = Field(None, description="Created before date")
    has_issues: Optional[bool] = Field(None, description="Filter by has issues")
    search: Optional[str] = Field(None, description="Search term")


class AnalysisStats(BaseModel):
    """Analysis statistics schema"""
    total_analyses: int = Field(..., description="Total analyses")
    completed_analyses: int = Field(..., description="Completed analyses")
    failed_analyses: int = Field(..., description="Failed analyses")
    average_score: float = Field(..., description="Average score")
    average_processing_time: float = Field(..., description="Average processing time")
    total_tokens_used: int = Field(..., description="Total tokens used")
    total_cost: float = Field(..., description="Total cost")
    analyses_by_language: Dict[str, int] = Field(..., description="Analyses by language")
    analyses_by_status: Dict[str, int] = Field(..., description="Analyses by status")


class AnalysisProgress(BaseModel):
    """Analysis progress schema"""
    analysis_id: int
    status: AnalysisStatus
    progress_percentage: int
    current_file: Optional[str] = None
    total_files: int
    processed_files: int
    estimated_time_remaining: Optional[str] = None


class Issue(BaseModel):
    """Issue schema"""
    id: Optional[int] = Field(None, description="Issue ID")
    severity: str = Field(..., description="Issue severity")
    type: str = Field(..., description="Issue type")
    message: str = Field(..., description="Issue message")
    file_path: Optional[str] = Field(None, description="File path")
    line_number: Optional[int] = Field(None, description="Line number")
    code_snippet: Optional[str] = Field(None, description="Code snippet")
    recommendation: Optional[str] = Field(None, description="Recommendation")


class AnalysisExportRequest(BaseModel):
    """Analysis export request schema"""
    format: str = Field(default="json", description="Export format")
    include_details: bool = Field(default=True, description="Include detailed findings")
    include_code_snippets: bool = Field(default=True, description="Include code snippets")
    include_metrics: bool = Field(default=True, description="Include metrics")


class AnalysisConfigTemplate(BaseModel):
    """Analysis configuration template schema"""
    name: str = Field(..., description="Template name")
    description: Optional[str] = Field(None, description="Template description")
    configuration: Dict[str, Any] = Field(..., description="Configuration")
    is_public: bool = Field(default=False, description="Is public template")


class BatchAnalysisRequest(BaseModel):
    """Batch analysis request schema"""
    repository_url: str = Field(..., description="Repository URL")
    file_patterns: Optional[List[str]] = Field(default_factory=list, description="File patterns to include")
    exclude_patterns: Optional[List[str]] = Field(default_factory=list, description="File patterns to exclude")
    prompt_id: int = Field(..., description="Prompt ID to use")
    configuration: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Analysis configuration")


class BatchAnalysisResponse(BaseModel):
    """Batch analysis response schema"""
    batch_id: str = Field(..., description="Batch ID")
    analysis_ids: List[int] = Field(..., description="Analysis IDs")
    total_files: int = Field(..., description="Total files")
    estimated_time: Optional[str] = Field(None, description="Estimated time")


class AnalysisWebhookRequest(BaseModel):
    """Analysis webhook request schema"""
    webhook_url: str = Field(..., description="Webhook URL")
    events: List[str] = Field(..., description="Events to subscribe to")
    secret: Optional[str] = Field(None, description="Webhook secret")


class AnalysisWebhookResponse(BaseModel):
    """Analysis webhook response schema"""
    id: int = Field(..., description="Webhook ID")
    webhook_url: str = Field(..., description="Webhook URL")
    events: List[str] = Field(..., description="Subscribed events")
    is_active: bool = Field(..., description="Is active")
    created_at: datetime = Field(..., description="Creation time")

    class Config:
        from_attributes = True


class AnalysisComparison(BaseModel):
    """Analysis comparison schema"""
    baseline_analysis_id: int = Field(..., description="Baseline analysis ID")
    comparison_analysis_id: int = Field(..., description="Comparison analysis ID")
    differences: Dict[str, Any] = Field(..., description="Differences")
    improvements: List[Dict[str, Any]] = Field(..., description="Improvements")
    regressions: List[Dict[str, Any]] = Field(..., description="Regressions")