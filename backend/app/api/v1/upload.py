"""
File upload API endpoints for VerificAI Backend
"""

import os
import uuid
import shutil
from typing import List, Optional
from pathlib import Path
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.uploaded_file import UploadedFile, FileStatus, ProcessingStatus
from app.schemas.upload import (
    FileUploadRequest, FileUploadResponse, FileListResponse,
    FileUpdateRequest, FileDeleteRequest, FileDeleteResponse,
    FileStatsResponse, UploadValidationResponse, ValidationError
)
from app.core.logging import app_logger as logger

router = APIRouter(prefix="/upload", tags=["upload"])


# Constants
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_EXTENSIONS = {
    'js', 'jsx', 'ts', 'tsx', 'py', 'java', 'c', 'cpp', 'cxx', 'cc',
    'h', 'hpp', 'cs', 'go', 'rs', 'rb', 'php', 'swift', 'kt', 'scala',
    'm', 'sh', 'bash', 'zsh', 'sql', 'html', 'css', 'scss', 'sass', 'less',
    'json', 'xml', 'yaml', 'yml', 'toml', 'ini', 'conf', 'config', 'md', 'txt'
}
UPLOAD_DIR = Path("uploads")


def ensure_upload_dir():
    """Ensure upload directory exists"""
    UPLOAD_DIR.mkdir(exist_ok=True)


def validate_file(file: UploadFile, user_id: int) -> UploadValidationResponse:
    """Validate uploaded file"""
    errors = []
    warnings = []

    # Check file size
    if file.size and file.size > MAX_FILE_SIZE:
        errors.append(ValidationError(
            field="size",
            message=f"File size {file.size} exceeds maximum allowed size {MAX_FILE_SIZE}"
        ))

    # Check file extension
    file_ext = Path(file.filename).suffix.lower().lstrip('.')
    if file_ext not in ALLOWED_EXTENSIONS:
        errors.append(ValidationError(
            field="extension",
            message=f"File extension .{file_ext} is not supported"
        ))

    # Check for duplicate files
    if file.filename:
        # This would require database check, implemented in upload endpoint
        pass

    return UploadValidationResponse(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        max_file_size=MAX_FILE_SIZE,
        allowed_extensions=list(ALLOWED_EXTENSIONS)
    )


def get_file_upload_path(file_id: str, original_name: str) -> Path:
    """Get file upload path"""
    safe_name = "".join(c for c in original_name if c.isalnum() or c in (' ', '-', '_', '.'))
    return UPLOAD_DIR / f"{file_id}_{safe_name}"


@router.post("/validate", response_model=UploadValidationResponse)
async def validate_upload(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Validate file before upload"""
    return validate_file(file, current_user.id)


@router.post("/", response_model=FileUploadResponse)
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    file_id: str = Form(...),
    original_name: str = Form(...),
    relative_path: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a single file"""
    ensure_upload_dir()

    # Validate file
    validation = validate_file(file, current_user.id)
    if not validation.is_valid:
        raise HTTPException(
            status_code=400,
            detail=f"File validation failed: {validation.errors[0].message}"
        )

    try:
        # Generate file path
        file_upload_path = get_file_upload_path(file_id, original_name)

        # Save file to disk
        with open(file_upload_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Create database record
        uploaded_file = UploadedFile(
            file_id=file_id,
            original_name=original_name,
            file_path=str(file_upload_path.relative_to(Path.cwd())),
            relative_path=relative_path,
            file_size=file.size or 0,
            mime_type=file.content_type or "application/octet-stream",
            file_extension=Path(original_name).suffix.lower().lstrip('.'),
            storage_path=str(file_upload_path.absolute()),
            status=FileStatus.COMPLETED,
            upload_progress=100,
            user_id=current_user.id
        )

        db.add(uploaded_file)
        db.commit()
        db.refresh(uploaded_file)

        # Add background task for file processing
        background_tasks.add_task(process_uploaded_file, uploaded_file.id, db)

        logger.info(f"File uploaded successfully: {file_id} by user {current_user.id}")

        return FileUploadResponse(
            file_id=uploaded_file.file_id,
            original_name=uploaded_file.original_name,
            file_path=uploaded_file.file_path,
            file_size=uploaded_file.file_size,
            mime_type=uploaded_file.mime_type,
            status=uploaded_file.status,
            upload_progress=uploaded_file.upload_progress,
            message="File uploaded successfully",
            upload_date=uploaded_file.created_at
        )

    except Exception as e:
        logger.error(f"Error uploading file {file_id}: {str(e)}")

        # Clean up uploaded file if database operation failed
        if file_upload_path.exists():
            file_upload_path.unlink()

        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")


async def process_uploaded_file(file_id: int, db: Session):
    """Process uploaded file in background"""
    try:
        # Get file from database
        uploaded_file = db.query(UploadedFile).filter(UploadedFile.id == file_id).first()
        if not uploaded_file:
            return

        # Update processing status
        uploaded_file.processing_status = ProcessingStatus.PROCESSING
        uploaded_file.is_processed = False
        db.commit()

        # Analyze file
        try:
            # Detect language
            detected_language = uploaded_file.get_language_from_extension()
            if detected_language:
                uploaded_file.language_detected = detected_language

            # Count lines (simplified - in production would use proper parsing)
            try:
                with open(uploaded_file.storage_path, 'r', encoding='utf-8') as f:
                    line_count = sum(1 for _ in f)
                uploaded_file.line_count = line_count
            except Exception:
                pass  # Skip line count for binary files or encoding issues

            # Calculate complexity (simplified placeholder)
            if line_count:
                if line_count < 50:
                    complexity = "1.0"
                elif line_count < 200:
                    complexity = "3.0"
                elif line_count < 500:
                    complexity = "5.0"
                elif line_count < 1000:
                    complexity = "7.0"
                else:
                    complexity = "9.0"
                uploaded_file.complexity_score = complexity

            # Mark as processed
            uploaded_file.processing_status = ProcessingStatus.COMPLETED
            uploaded_file.is_processed = True

            logger.info(f"File processed successfully: {uploaded_file.file_id}")

        except Exception as e:
            uploaded_file.processing_status = ProcessingStatus.ERROR
            uploaded_file.processing_error = str(e)
            logger.error(f"Error processing file {uploaded_file.file_id}: {str(e)}")

        db.commit()

    except Exception as e:
        logger.error(f"Error in background processing for file {file_id}: {str(e)}")


@router.get("/", response_model=FileListResponse)
async def list_files(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[FileStatus] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List uploaded files"""
    query = db.query(UploadedFile).filter(UploadedFile.user_id == current_user.id)

    if status:
        query = query.filter(UploadedFile.status == status)

    if search:
        query = query.filter(
            or_(
                UploadedFile.original_name.ilike(f"%{search}%"),
                UploadedFile.relative_path.ilike(f"%{search}%")
            )
        )

    total = query.count()
    files = query.order_by(UploadedFile.created_at.desc()).offset(skip).limit(limit).all()

    total_size = sum(f.file_size for f in files)

    file_responses = []
    for file in files:
        file_responses.append(FileUploadResponse(
            file_id=file.file_id,
            original_name=file.original_name,
            file_path=file.file_path,
            file_size=file.file_size,
            mime_type=file.mime_type,
            status=file.status,
            upload_progress=file.upload_progress,
            message="File listed successfully",
            upload_date=file.created_at
        ))

    return FileListResponse(
        files=file_responses,
        total_count=total,
        total_size=total_size
    )


@router.get("/{file_id}", response_model=FileUploadResponse)
async def get_file(
    file_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get file details"""
    file = db.query(UploadedFile).filter(
        and_(
            UploadedFile.file_id == file_id,
            UploadedFile.user_id == current_user.id
        )
    ).first()

    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    return FileUploadResponse(
        file_id=file.file_id,
        original_name=file.original_name,
        file_path=file.file_path,
        file_size=file.file_size,
        mime_type=file.mime_type,
        status=file.status,
        upload_progress=file.upload_progress,
        message="File retrieved successfully",
        upload_date=file.created_at
    )


@router.put("/{file_id}", response_model=FileUploadResponse)
async def update_file(
    file_id: str,
    update_data: FileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update file metadata"""
    file = db.query(UploadedFile).filter(
        and_(
            UploadedFile.file_id == file_id,
            UploadedFile.user_id == current_user.id
        )
    ).first()

    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    # Update fields
    update_dict = update_data.dict(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(file, field, value)

    file.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(file)

    return FileUploadResponse(
        file_id=file.file_id,
        original_name=file.original_name,
        file_path=file.file_path,
        file_size=file.file_size,
        mime_type=file.mime_type,
        status=file.status,
        upload_progress=file.upload_progress,
        message="File updated successfully",
        upload_date=file.created_at
    )


@router.delete("/", response_model=FileDeleteResponse)
async def delete_files(
    delete_request: FileDeleteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete multiple files"""
    deleted_files = []
    failed_files = []

    for file_id in delete_request.file_ids:
        try:
            file = db.query(UploadedFile).filter(
                and_(
                    UploadedFile.file_id == file_id,
                    UploadedFile.user_id == current_user.id
                )
            ).first()

            if not file:
                failed_files.append(file_id)
                continue

            # Delete physical file
            if Path(file.storage_path).exists():
                Path(file.storage_path).unlink()

            # Delete database record
            db.delete(file)
            deleted_files.append(file_id)

        except Exception as e:
            logger.error(f"Error deleting file {file_id}: {str(e)}")
            failed_files.append(file_id)

    db.commit()

    return FileDeleteResponse(
        deleted_files=deleted_files,
        failed_files=failed_files,
        message=f"Deleted {len(deleted_files)} files, {len(failed_files)} failed"
    )


@router.get("/stats/", response_model=FileStatsResponse)
async def get_file_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get file statistics"""
    files = db.query(UploadedFile).filter(UploadedFile.user_id == current_user.id).all()

    # Basic stats
    total_files = len(files)
    total_size = sum(f.file_size for f in files)

    # Status counts
    status_counts = {}
    for status in FileStatus:
        status_counts[status.value] = sum(1 for f in files if f.status == status)

    # File type counts
    file_type_counts = {}
    for file in files:
        ext = file.file_extension or 'unknown'
        file_type_counts[ext] = file_type_counts.get(ext, 0) + 1

    # User counts (for admin view)
    user_counts = {}
    if current_user.is_admin:
        from sqlalchemy import func
        user_stats = db.query(
            UploadedFile.user_id,
            func.count(UploadedFile.id).label('count')
        ).group_by(UploadedFile.user_id).all()
        user_counts = {str(user_id): count for user_id, count in user_stats}

    # Recent uploads
    recent_uploads = [
        {
            'file_id': f.file_id,
            'original_name': f.original_name,
            'file_size': f.file_size,
            'status': f.status,
            'upload_date': f.created_at.isoformat()
        }
        for f in sorted(files, key=lambda x: x.created_at, reverse=True)[:10]
    ]

    return FileStatsResponse(
        total_files=total_files,
        total_size=total_size,
        status_counts=status_counts,
        file_type_counts=file_type_counts,
        user_counts=user_counts,
        recent_uploads=recent_uploads
    )