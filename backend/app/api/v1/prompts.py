"""
Prompt management endpoints for VerificAI Backend
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, CommonQueryParams, get_pagination_params
from app.models.user import User
from app.models.prompt import Prompt, PromptStatus, PromptCategory
from app.schemas.prompt import (
    PromptCreate, PromptUpdate, PromptResponse, PromptListResponse,
    PromptSearchFilters, PromptTestRequest, PromptTestResponse,
    PromptCloneRequest, PromptValidationResult
)
from app.schemas.common import PaginatedResponse

router = APIRouter()


@router.post("/", response_model=PromptResponse)
def create_prompt(
    prompt_data: PromptCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Create a new prompt"""
    prompt = Prompt(**prompt_data.dict(), author_id=current_user.id)
    db.add(prompt)
    db.commit()
    db.refresh(prompt)

    return prompt


@router.get("/", response_model=PaginatedResponse[PromptResponse])
def list_prompts(
    params: CommonQueryParams = Depends(),
    filters: PromptSearchFilters = Depends(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """List prompts with filtering and pagination"""
    query = db.query(Prompt)

    # Apply filters
    if filters.category:
        query = query.filter(Prompt.category == filters.category)
    if filters.status:
        query = query.filter(Prompt.status == filters.status)
    if filters.is_public is not None:
        query = query.filter(Prompt.is_public == filters.is_public)
    if filters.is_featured is not None:
        query = query.filter(Prompt.is_featured == filters.is_featured)
    if filters.author_id:
        query = query.filter(Prompt.author_id == filters.author_id)
    if filters.supported_language:
        # Simple contains check - in production, use JSON operations
        query = query.filter(Prompt.supported_languages.contains(filters.supported_language))
    if filters.supported_file_type:
        query = query.filter(Prompt.supported_file_types.contains(filters.supported_file_type))
    if filters.search:
        query = query.filter(
            Prompt.name.contains(filters.search) |
            Prompt.description.contains(filters.search)
        )

    # Filter by visibility: users can see their own prompts + public prompts
    # Admins can see all prompts
    if not current_user.is_admin:
        query = query.filter(
            (Prompt.author_id == current_user.id) |
            (Prompt.is_public == True)
        )

    # Get total count
    total = query.count()

    # Apply sorting
    if params.sort_by:
        sort_column = getattr(Prompt, params.sort_by, None)
        if sort_column:
            if params.sort_order == "desc":
                query = query.order_by(sort_column.desc())
            else:
                query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(Prompt.created_at.desc())

    # Apply pagination
    prompts = query.offset(params.skip).limit(params.limit).all()

    return PaginatedResponse(
        items=prompts,
        total=total,
        skip=params.skip,
        limit=params.limit,
        pages=(total + params.limit - 1) // params.limit,
        current_page=(params.skip // params.limit) + 1,
        has_next=params.skip + params.limit < total,
        has_prev=params.skip > 0
    )


@router.get("/{prompt_id}", response_model=PromptResponse)
def get_prompt(
    prompt_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get prompt by ID"""
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prompt not found"
        )

    # Check permissions
    if not prompt.is_public and prompt.author_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    return prompt


@router.put("/{prompt_id}", response_model=PromptResponse)
def update_prompt(
    prompt_id: int,
    prompt_data: PromptUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Update prompt"""
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prompt not found"
        )

    # Check permissions
    if prompt.author_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    # Update fields
    for field, value in prompt_data.dict(exclude_unset=True).items():
        setattr(prompt, field, value)

    db.commit()
    db.refresh(prompt)

    return prompt


@router.delete("/{prompt_id}", response_model=dict)
def delete_prompt(
    prompt_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Delete prompt"""
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prompt not found"
        )

    # Check permissions
    if prompt.author_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    db.delete(prompt)
    db.commit()

    return {"message": "Prompt deleted successfully"}


@router.post("/{prompt_id}/test", response_model=PromptTestResponse)
def test_prompt(
    prompt_id: int,
    test_data: PromptTestRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Test prompt with sample code"""
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prompt not found"
        )

    # Check permissions
    if not prompt.is_public and prompt.author_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    # TODO: Implement actual testing logic
    # This is a placeholder response
    return PromptTestResponse(
        success=True,
        response="Test response - this is a placeholder",
        tokens_used=100,
        processing_time=2.5,
        cost_estimate=0.01
    )


@router.post("/{prompt_id}/clone", response_model=PromptResponse)
def clone_prompt(
    prompt_id: int,
    clone_data: PromptCloneRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Clone prompt"""
    original_prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if not original_prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prompt not found"
        )

    # Check permissions
    if not original_prompt.is_public and original_prompt.author_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    # Create clone
    new_prompt = Prompt(
        name=clone_data.new_name,
        description=clone_data.new_description or original_prompt.description,
        category=original_prompt.category,
        system_prompt=original_prompt.system_prompt,
        user_prompt_template=original_prompt.user_prompt_template,
        output_format_instructions=original_prompt.output_format_instructions,
        temperature=original_prompt.temperature,
        max_tokens=original_prompt.max_tokens,
        model_name=original_prompt.model_name,
        tags=original_prompt.tags,
        supported_languages=original_prompt.supported_languages,
        supported_file_types=original_prompt.supported_file_types,
        author_id=current_user.id
    )

    db.add(new_prompt)
    db.commit()
    db.refresh(new_prompt)

    return new_prompt


@router.post("/{prompt_id}/validate", response_model=PromptValidationResult)
def validate_prompt(
    prompt_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Validate prompt"""
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prompt not found"
        )

    # Check permissions
    if prompt.author_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    # TODO: Implement actual validation logic
    # This is a placeholder response
    return PromptValidationResult(
        is_valid=True,
        errors=[],
        warnings=["This is a placeholder validation"],
        suggestions=["Consider adding more specific tags"]
    )


@router.post("/{prompt_id}/publish", response_model=PromptResponse)
def publish_prompt(
    prompt_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Publish prompt (make public)"""
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prompt not found"
        )

    # Check permissions
    if prompt.author_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    prompt.is_public = True
    prompt.status = PromptStatus.ACTIVE
    db.commit()
    db.refresh(prompt)

    return prompt


@router.post("/{prompt_id}/unpublish", response_model=PromptResponse)
def unpublish_prompt(
    prompt_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Unpublish prompt (make private)"""
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prompt not found"
        )

    # Check permissions
    if prompt.author_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    prompt.is_public = False
    db.commit()
    db.refresh(prompt)

    return prompt


@router.get("/categories", response_model=List[str])
def get_prompt_categories(
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get available prompt categories"""
    return [category.value for category in PromptCategory]


@router.get("/statuses", response_model=List[str])
def get_prompt_statuses(
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get available prompt statuses"""
    return [status.value for status in PromptStatus]


@router.post("/import", response_model=PromptResponse)
def import_prompt(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Import prompt from file"""
    # TODO: Implement actual import logic
    # This is a placeholder response
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Import functionality not yet implemented"
    )


@router.get("/{prompt_id}/export")
def export_prompt(
    prompt_id: int,
    format: str = "json",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Export prompt"""
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prompt not found"
        )

    # Check permissions
    if not prompt.is_public and prompt.author_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    # TODO: Implement actual export logic
    # This is a placeholder response
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Export functionality not yet implemented"
    )