"""
Source code endpoints for VerificAI Backend - Updated
"""

from typing import List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.dependencies import get_current_user, CommonQueryParams, get_pagination_params
from app.models.user import User
from app.models.source_code import SourceCode, SourceCodeStatus
from app.schemas.common import PaginatedResponse

router = APIRouter()


# Pydantic schemas for request/response
class SourceCodeCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500, description="Title of the source code")
    description: Optional[str] = Field(None, max_length=2000, description="Description of the source code")
    content: str = Field(..., min_length=1, description="Source code content")
    file_name: str = Field(..., min_length=1, max_length=500, description="File name")
    file_extension: str = Field(..., min_length=1, max_length=10, description="File extension")
    programming_language: Optional[str] = Field(None, max_length=50, description="Programming language")
    category: Optional[str] = Field(None, max_length=100, description="Category")
    tags: Optional[List[str]] = Field(default=[], description="List of tags")
    code_metadata: Optional[dict] = Field(default={}, description="Additional metadata")
    is_public: bool = Field(default=False, description="Whether the source code is public")
    is_template: bool = Field(default=False, description="Whether this is a template")


class SourceCodeUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500, description="Title of the source code")
    description: Optional[str] = Field(None, max_length=2000, description="Description of the source code")
    content: Optional[str] = Field(None, min_length=1, description="Source code content")
    programming_language: Optional[str] = Field(None, max_length=50, description="Programming language")
    category: Optional[str] = Field(None, max_length=100, description="Category")
    tags: Optional[List[str]] = Field(None, description="List of tags")
    code_metadata: Optional[dict] = Field(None, description="Additional metadata")
    is_public: Optional[bool] = Field(None, description="Whether the source code is public")
    is_template: Optional[bool] = Field(None, description="Whether this is a template")


class SourceCodeResponse(BaseModel):
    id: int
    code_id: str
    title: str
    description: Optional[str]
    file_name: str
    file_extension: str
    programming_language: Optional[str]
    line_count: Optional[int]
    character_count: Optional[int]
    size_bytes: Optional[int]
    language_detected: Optional[str]
    complexity_score: Optional[str]
    category: Optional[str]
    tags: List[str]
    code_metadata: Optional[dict]
    status: str
    is_public: bool
    is_template: bool
    is_processed: bool
    processing_status: Optional[str]
    processing_error: Optional[str]
    analysis_id: Optional[str]
    last_analyzed_at: Optional[str]
    user_id: int
    access_level: str
    created_at: str
    updated_at: str
    size_info: Optional[dict] = None

    class Config:
        from_attributes = True


class SourceCodeListResponse(BaseModel):
    items: List[SourceCodeResponse]
    total: int
    skip: int
    limit: int
    pages: int
    current_page: int
    has_next: bool
    has_prev: bool


@router.post("/", response_model=SourceCodeResponse)
def create_source_code(
    source_code_data: SourceCodeCreate,
    db: Session = Depends(get_db)
) -> Any:
    # Temporarily remove authentication for testing
    # current_user: User = Depends(get_current_user),
    """Create a new source code entry"""

    # Validate content size (1GB limit for PostgreSQL TEXT)
    content_size_bytes = len(source_code_data.content.encode('utf-8'))
    if content_size_bytes > 1024 * 1024 * 1024:  # 1GB
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Source code content exceeds the 1GB limit"
        )

    # Create source code object
    source_code = SourceCode(
        title=source_code_data.title,
        description=source_code_data.description,
        content=source_code_data.content,
        file_name=source_code_data.file_name,
        file_extension=source_code_data.file_extension,
        programming_language=source_code_data.programming_language,
        category=source_code_data.category,
        code_metadata=source_code_data.code_metadata,
        is_public=source_code_data.is_public,
        is_template=source_code_data.is_template,
        user_id=1,  # Temporary: fixed user ID for testing
        processing_status="pending",
        status=SourceCodeStatus.ACTIVE
    )

    # Set tags if provided
    if source_code_data.tags:
        source_code.set_tags_list(source_code_data.tags)

    # Calculate metrics
    source_code.calculate_metrics()

    # Auto-detect programming language if not provided
    if not source_code.programming_language:
        source_code.language_detected = source_code.detect_language_from_extension()
        source_code.programming_language = source_code.language_detected

    db.add(source_code)
    db.commit()
    db.refresh(source_code)

    return source_code


@router.get("/", response_model=PaginatedResponse[SourceCodeResponse])
def list_source_codes(
    params: CommonQueryParams = Depends(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """List source codes with filtering and pagination"""
    query = db.query(SourceCode)

    # Users can only see their own source codes unless admin
    if not current_user.is_admin:
        query = query.filter(SourceCode.user_id == current_user.id)

    # Apply search filter
    if params.search:
        query = query.filter(
            SourceCode.title.contains(params.search) |
            SourceCode.description.contains(params.search) |
            SourceCode.file_name.contains(params.search)
        )

    # Get total count
    total = query.count()

    # Apply sorting
    if params.sort_by:
        sort_column = getattr(SourceCode, params.sort_by, None)
        if sort_column:
            if params.sort_order == "desc":
                query = query.order_by(sort_column.desc())
            else:
                query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(SourceCode.created_at.desc())

    # Apply pagination
    source_codes = query.offset(params.skip).limit(params.limit).all()

    return PaginatedResponse(
        items=source_codes,
        total=total,
        skip=params.skip,
        limit=params.limit,
        pages=(total + params.limit - 1) // params.limit,
        current_page=(params.skip // params.limit) + 1,
        has_next=params.skip + params.limit < total,
        has_prev=params.skip > 0
    )


@router.get("/{source_code_id}", response_model=SourceCodeResponse)
def get_source_code(
    source_code_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get source code by ID"""
    source_code = db.query(SourceCode).filter(SourceCode.id == source_code_id).first()
    if not source_code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source code not found"
        )

    # Check permissions
    if source_code.user_id != current_user.id and not current_user.is_admin and not source_code.is_public:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    # Include size info
    source_code.size_info = source_code.get_size_info()

    return source_code


@router.get("/{source_code_id}/content")
def get_source_code_content(
    source_code_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get source code content by ID"""
    source_code = db.query(SourceCode).filter(SourceCode.id == source_code_id).first()
    if not source_code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source code not found"
        )

    # Check permissions
    if source_code.user_id != current_user.id and not current_user.is_admin and not source_code.is_public:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    return {
        "code_id": source_code.code_id,
        "title": source_code.title,
        "content": source_code.content,
        "file_name": source_code.file_name,
        "file_extension": source_code.file_extension,
        "programming_language": source_code.get_programming_language(),
        "line_count": source_code.line_count,
        "size_bytes": source_code.size_bytes,
        "size_info": source_code.get_size_info()
    }


@router.put("/{source_code_id}", response_model=SourceCodeResponse)
def update_source_code(
    source_code_id: int,
    source_code_data: SourceCodeUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Update source code"""
    source_code = db.query(SourceCode).filter(SourceCode.id == source_code_id).first()
    if not source_code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source code not found"
        )

    # Check permissions
    if source_code.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    # Update fields
    update_data = source_code_data.dict(exclude_unset=True)

    # Handle tags separately
    if 'tags' in update_data:
        source_code.set_tags_list(update_data.pop('tags'))

    # Validate content size if provided
    if 'content' in update_data:
        content_size_bytes = len(update_data['content'].encode('utf-8'))
        if content_size_bytes > 1024 * 1024 * 1024:  # 1GB
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Source code content exceeds the 1GB limit"
            )

    for field, value in update_data.items():
        setattr(source_code, field, value)

    # Recalculate metrics if content was updated
    if 'content' in update_data:
        source_code.calculate_metrics()

    # Auto-detect programming language if not provided
    if not source_code.programming_language:
        source_code.language_detected = source_code.detect_language_from_extension()
        source_code.programming_language = source_code.language_detected

    db.commit()
    db.refresh(source_code)

    return source_code


@router.delete("/{source_code_id}", response_model=dict)
def delete_source_code(
    source_code_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Delete source code"""
    source_code = db.query(SourceCode).filter(SourceCode.id == source_code_id).first()
    if not source_code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source code not found"
        )

    # Check permissions
    if source_code.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    # Soft delete by updating status
    source_code.status = SourceCodeStatus.DELETED
    db.commit()

    return {"message": "Source code deleted successfully"}


@router.get("/stats/overview", response_model=dict)
def get_source_code_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get source code statistics"""
    query = db.query(SourceCode)

    # Users can only see their own stats unless admin
    if not current_user.is_admin:
        query = query.filter(SourceCode.user_id == current_user.id)

    total_codes = query.count()
    active_codes = query.filter(SourceCode.status == SourceCodeStatus.ACTIVE).count()
    processed_codes = query.filter(SourceCode.is_processed == True).count()
    pending_codes = query.filter(SourceCode.processing_status == "pending").count()

    # Calculate total size
    all_codes = query.all()
    total_size_bytes = sum(code.size_bytes or 0 for code in all_codes)
    total_size_mb = total_size_bytes / (1024 * 1024)

    # Group by programming language
    language_counts = {}
    for code in all_codes:
        lang = code.get_programming_language()
        language_counts[lang] = language_counts.get(lang, 0) + 1

    return {
        "total_codes": total_codes,
        "active_codes": active_codes,
        "processed_codes": processed_codes,
        "pending_codes": pending_codes,
        "total_size_bytes": total_size_bytes,
        "total_size_mb": round(total_size_mb, 2),
        "language_counts": language_counts,
        "size_limit_percentage": round((total_size_bytes / (1024 * 1024 * 1024)) * 100, 6)  # percentage of 1GB limit
    }