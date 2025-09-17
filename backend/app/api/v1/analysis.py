"""
Analysis endpoints for VerificAI Backend
"""

from typing import List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, CommonQueryParams, get_pagination_params
from app.models.user import User
from app.models.analysis import Analysis, AnalysisStatus
from app.schemas.analysis import (
    AnalysisCreate, AnalysisUpdate, AnalysisResponse, AnalysisListResponse,
    AnalysisResultResponse, AnalysisSearchFilters, AnalysisStats,
    BatchAnalysisRequest, BatchAnalysisResponse
)
from app.schemas.common import PaginatedResponse

router = APIRouter()


@router.post("/", response_model=AnalysisResponse)
def create_analysis(
    analysis_data: AnalysisCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Create a new analysis"""
    # Validate prompt exists and user has access
    from app.models.prompt import Prompt
    prompt = db.query(Prompt).filter(Prompt.id == analysis_data.prompt_id).first()
    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prompt not found"
        )

    if not prompt.is_public and prompt.author_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to prompt"
        )

    # Create analysis
    analysis = Analysis(
        **analysis_data.dict(),
        user_id=current_user.id,
        status=AnalysisStatus.PENDING
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    # Start background processing
    background_tasks.add_task(process_analysis, analysis.id, db)

    return analysis


@router.get("/", response_model=PaginatedResponse[AnalysisResponse])
def list_analyses(
    params: CommonQueryParams = Depends(),
    filters: AnalysisSearchFilters = Depends(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """List analyses with filtering and pagination"""
    query = db.query(Analysis)

    # Apply filters
    if filters.status:
        query = query.filter(Analysis.status == filters.status)
    if filters.user_id:
        # Users can only see their own analyses unless admin
        if filters.user_id != current_user.id and not current_user.is_admin:
            query = query.filter(Analysis.user_id == current_user.id)
        else:
            query = query.filter(Analysis.user_id == filters.user_id)
    else:
        # Users can only see their own analyses unless admin
        if not current_user.is_admin:
            query = query.filter(Analysis.user_id == current_user.id)

    if filters.prompt_id:
        query = query.filter(Analysis.prompt_id == filters.prompt_id)
    if filters.language:
        query = query.filter(Analysis.language == filters.language)
    if filters.min_score is not None:
        query = query.filter(Analysis.overall_score >= filters.min_score)
    if filters.max_score is not None:
        query = query.filter(Analysis.overall_score <= filters.max_score)
    if filters.search:
        query = query.filter(
            Analysis.name.contains(filters.search) |
            Analysis.description.contains(filters.search)
        )

    # Get total count
    total = query.count()

    # Apply sorting
    if params.sort_by:
        sort_column = getattr(Analysis, params.sort_by, None)
        if sort_column:
            if params.sort_order == "desc":
                query = query.order_by(sort_column.desc())
            else:
                query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(Analysis.created_at.desc())

    # Apply pagination
    analyses = query.offset(params.skip).limit(params.limit).all()

    return PaginatedResponse(
        items=analyses,
        total=total,
        skip=params.skip,
        limit=params.limit,
        pages=(total + params.limit - 1) // params.limit,
        current_page=(params.skip // params.limit) + 1,
        has_next=params.skip + params.limit < total,
        has_prev=params.skip > 0
    )


@router.get("/{analysis_id}", response_model=AnalysisResponse)
def get_analysis(
    analysis_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get analysis by ID"""
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )

    # Check permissions
    if analysis.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    return analysis


@router.get("/{analysis_id}/result", response_model=AnalysisResultResponse)
def get_analysis_result(
    analysis_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get analysis result"""
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )

    # Check permissions
    if analysis.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    if not analysis.result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis result not available"
        )

    return analysis.result


@router.put("/{analysis_id}", response_model=AnalysisResponse)
def update_analysis(
    analysis_id: int,
    analysis_data: AnalysisUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Update analysis"""
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )

    # Check permissions
    if analysis.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    # Can only update pending analyses
    if analysis.status != AnalysisStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only update pending analyses"
        )

    # Update fields
    for field, value in analysis_data.dict(exclude_unset=True).items():
        setattr(analysis, field, value)

    db.commit()
    db.refresh(analysis)

    return analysis


@router.delete("/{analysis_id}", response_model=dict)
def delete_analysis(
    analysis_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Delete analysis"""
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )

    # Check permissions
    if analysis.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    # Can only delete pending or completed analyses
    if analysis.status == AnalysisStatus.PROCESSING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete analysis while processing"
        )

    db.delete(analysis)
    db.commit()

    return {"message": "Analysis deleted successfully"}


@router.post("/{analysis_id}/cancel", response_model=dict)
def cancel_analysis(
    analysis_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Cancel analysis"""
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )

    # Check permissions
    if analysis.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    # Can only cancel processing analyses
    if analysis.status != AnalysisStatus.PROCESSING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only cancel processing analyses"
        )

    analysis.cancel_processing()
    db.commit()

    return {"message": "Analysis cancelled successfully"}


@router.post("/{analysis_id}/restart", response_model=AnalysisResponse)
def restart_analysis(
    analysis_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Restart analysis"""
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )

    # Check permissions
    if analysis.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    # Can only restart failed or cancelled analyses
    if analysis.status not in [AnalysisStatus.FAILED, AnalysisStatus.CANCELLED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only restart failed or cancelled analyses"
        )

    # Reset analysis status
    analysis.status = AnalysisStatus.PENDING
    analysis.progress_percentage = 0
    analysis.error_message = None
    analysis.started_at = None
    analysis.completed_at = None

    db.commit()

    # Start background processing
    background_tasks.add_task(process_analysis, analysis.id, db)

    return analysis


@router.post("/batch", response_model=BatchAnalysisResponse)
def create_batch_analysis(
    batch_data: BatchAnalysisRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Create batch analysis"""
    # TODO: Implement actual batch analysis logic
    # This is a placeholder response
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Batch analysis functionality not yet implemented"
    )


@router.get("/stats", response_model=AnalysisStats)
def get_analysis_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get analysis statistics"""
    # Users can only see their own stats unless admin
    if current_user.is_admin:
        query = db.query(Analysis)
    else:
        query = db.query(Analysis).filter(Analysis.user_id == current_user.id)

    total_analyses = query.count()
    completed_analyses = query.filter(Analysis.status == AnalysisStatus.COMPLETED).count()
    failed_analyses = query.filter(Analysis.status == AnalysisStatus.FAILED).count()

    # Calculate average score for completed analyses
    completed_query = query.filter(Analysis.status == AnalysisStatus.COMPLETED)
    avg_score = completed_query.with_entities(Analysis.overall_score).all()
    avg_score = sum([score[0] or 0 for score in avg_score]) / len(avg_score) if avg_score else 0

    return AnalysisStats(
        total_analyses=total_analyses,
        completed_analyses=completed_analyses,
        failed_analyses=failed_analyses,
        average_score=avg_score,
        average_processing_time=0.0,  # TODO: Calculate actual processing time
        total_tokens_used=0,  # TODO: Sum actual tokens used
        total_cost=0.0,  # TODO: Calculate actual cost
        analyses_by_language={},  # TODO: Group by language
        analyses_by_status={}  # TODO: Group by status
    )


@router.post("/upload", response_model=AnalysisResponse)
def upload_analysis_file(
    file: UploadFile = File(...),
    prompt_id: int = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = None
) -> Any:
    """Upload file for analysis"""
    # TODO: Implement actual file upload and analysis
    # This is a placeholder response
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="File upload functionality not yet implemented"
    )


# Background task for processing analysis
async def process_analysis(analysis_id: int, db: Session) -> None:
    """Process analysis in background"""
    from app.models.analysis import AnalysisResult

    try:
        # Get analysis
        analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
        if not analysis:
            return

        # Start processing
        analysis.start_processing()
        db.commit()

        # TODO: Implement actual analysis logic
        # This is a placeholder implementation
        import time
        time.sleep(2)  # Simulate processing

        # Create result
        result = AnalysisResult(
            analysis_id=analysis.id,
            summary="Sample analysis result",
            detailed_findings="Detailed findings would go here",
            recommendations="Recommendations would go here",
            score=85,
            confidence=0.9,
            model_used="gpt-4-turbo-preview",
            tokens_used=1000,
            processing_time="2.0",
            quality_score=85,
            security_score=90,
            performance_score=80,
            maintainability_score=85
        )

        db.add(result)
        db.commit()

        # Complete analysis
        analysis.complete_processing()
        analysis.calculate_scores()
        db.commit()

    except Exception as e:
        # Mark analysis as failed
        analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
        if analysis:
            analysis.fail_processing(str(e))
            db.commit()