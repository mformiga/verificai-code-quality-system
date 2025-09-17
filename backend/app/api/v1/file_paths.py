"""
API endpoints for file path management
"""

import logging
from typing import List
from uuid import uuid4
from datetime import datetime
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.file_path import FilePath
from app.schemas.file_path import (
    FilePathCreate,
    FilePathResponse,
    FilePathBulkCreate,
    FilePathBulkResponse,
    FilePathListResponse,
    FilePathUpdate
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/test")
async def test_endpoint():
    """Test endpoint to verify router is working"""
    return {"message": "File paths router is working!"}


@router.post("/bulk", response_model=FilePathBulkResponse)
async def create_file_paths_bulk(
    file_paths_data: FilePathBulkCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create multiple file paths at once"""
    try:
        created_paths = []
        errors = []

        for file_path_data in file_paths_data.file_paths:
            try:
                # Check if file path already exists
                existing_path = db.query(FilePath).filter(
                    FilePath.full_path == file_path_data.full_path,
                    FilePath.user_id == current_user.id
                ).first()

                if existing_path:
                    errors.append(f"File path already exists: {file_path_data.full_path}")
                    continue

                # Create new file path
                db_file_path = FilePath(
                    **file_path_data.dict(),
                    user_id=current_user.id
                )
                db.add(db_file_path)
                db.commit()
                db.refresh(db_file_path)
                created_paths.append(db_file_path)

                logger.info(f"File path created: {file_path_data.full_path} by user {current_user.id}")

            except Exception as e:
                logger.error(f"Error creating file path {file_path_data.full_path}: {str(e)}")
                errors.append(f"Failed to create path: {file_path_data.full_path} - {str(e)}")
                db.rollback()

        return FilePathBulkResponse(
            created_count=len(created_paths),
            file_paths=created_paths,
            errors=errors
        )

    except Exception as e:
        logger.error(f"Error in bulk file path creation: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/", response_model=FilePathResponse)
async def create_file_path(
    file_path_data: FilePathCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a single file path"""
    try:
        # Check if file path already exists
        existing_path = db.query(FilePath).filter(
            FilePath.full_path == file_path_data.full_path,
            FilePath.user_id == current_user.id
        ).first()

        if existing_path:
            raise HTTPException(status_code=400, detail="File path already exists")

        # Create new file path
        db_file_path = FilePath(
            **file_path_data.dict(),
            user_id=current_user.id
        )
        db.add(db_file_path)
        db.commit()
        db.refresh(db_file_path)

        logger.info(f"File path created: {file_path_data.full_path} by user {current_user.id}")

        return db_file_path

    except Exception as e:
        logger.error(f"Error creating file path: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/", response_model=FilePathListResponse)
async def get_file_paths(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    search: str = Query(None, description="Search in file names"),
    extension: str = Query(None, description="Filter by file extension"),
    folder: str = Query(None, description="Filter by folder path"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get file paths with pagination and filtering"""
    try:
        # Build query
        query = db.query(FilePath).filter(FilePath.user_id == current_user.id)

        # Apply filters
        if search:
            query = query.filter(FilePath.file_name.contains(search))
        if extension:
            query = query.filter(FilePath.file_extension == extension)
        if folder:
            query = query.filter(FilePath.folder_path.contains(folder))

        # Get total count
        total_count = query.count()
        total_pages = (total_count + per_page - 1) // per_page

        # Get paginated results
        file_paths = query.order_by(desc(FilePath.created_at))\
            .offset((page - 1) * per_page)\
            .limit(per_page)\
            .all()

        return FilePathListResponse(
            file_paths=file_paths,
            total_count=total_count,
            page=page,
            per_page=per_page,
            total_pages=total_pages
        )

    except Exception as e:
        logger.error(f"Error getting file paths: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{file_id}", response_model=FilePathResponse)
async def get_file_path(
    file_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific file path by ID"""
    try:
        file_path = db.query(FilePath).filter(
            FilePath.file_id == file_id,
            FilePath.user_id == current_user.id
        ).first()

        if not file_path:
            raise HTTPException(status_code=404, detail="File path not found")

        return file_path

    except Exception as e:
        logger.error(f"Error getting file path {file_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/{file_id}", response_model=FilePathResponse)
async def update_file_path(
    file_id: str,
    file_path_data: FilePathUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a file path"""
    try:
        file_path = db.query(FilePath).filter(
            FilePath.file_id == file_id,
            FilePath.user_id == current_user.id
        ).first()

        if not file_path:
            raise HTTPException(status_code=404, detail="File path not found")

        # Update fields
        update_data = file_path_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(file_path, field, value)

        file_path.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(file_path)

        logger.info(f"File path updated: {file_id} by user {current_user.id}")

        return file_path

    except Exception as e:
        logger.error(f"Error updating file path {file_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{file_id}")
async def delete_file_path(
    file_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a file path"""
    try:
        file_path = db.query(FilePath).filter(
            FilePath.file_id == file_id,
            FilePath.user_id == current_user.id
        ).first()

        if not file_path:
            raise HTTPException(status_code=404, detail="File path not found")

        db.delete(file_path)
        db.commit()

        logger.info(f"File path deleted: {file_id} by user {current_user.id}")

        return {"message": "File path deleted successfully"}

    except Exception as e:
        logger.error(f"Error deleting file path {file_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/")
async def delete_file_paths_bulk(
    file_ids: List[str] = [],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete multiple file paths or all if empty list"""
    try:
        # If empty list, delete all file paths for this user
        if not file_ids:
            file_paths = db.query(FilePath).filter(
                FilePath.user_id == current_user.id
            ).all()
        else:
            # Get specific file paths to delete
            file_paths = db.query(FilePath).filter(
                FilePath.file_id.in_(file_ids),
                FilePath.user_id == current_user.id
            ).all()

        if not file_paths:
            raise HTTPException(status_code=404, detail="No file paths found")

        # Delete file paths
        for file_path in file_paths:
            db.delete(file_path)

        db.commit()

        logger.info(f"Bulk deleted {len(file_paths)} file paths by user {current_user.id}")

        return {
            "message": f"Successfully deleted {len(file_paths)} file paths",
            "deleted_count": len(file_paths)
        }

    except Exception as e:
        logger.error(f"Error in bulk file path deletion: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/summary")
async def get_file_paths_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get summary statistics for file paths"""
    try:
        # Get total count
        total_count = db.query(FilePath).filter(
            FilePath.user_id == current_user.id
        ).count()

        # Get unique extensions
        extensions = db.query(
            FilePath.file_extension,
            func.count(FilePath.file_extension).label('count')
        ).filter(
            FilePath.user_id == current_user.id,
            FilePath.file_extension.isnot(None)
        ).group_by(FilePath.file_extension).all()

        # Get unique folders
        folders = db.query(
            FilePath.folder_path,
            func.count(FilePath.folder_path).label('count')
        ).filter(
            FilePath.user_id == current_user.id
        ).group_by(FilePath.folder_path).all()

        # Get total size
        total_size = db.query(
            func.sum(FilePath.file_size)
        ).filter(
            FilePath.user_id == current_user.id,
            FilePath.file_size.isnot(None)
        ).scalar() or 0

        return {
            "total_count": total_count,
            "total_size": total_size,
            "unique_extensions": [
                {"extension": ext.file_extension, "count": ext.count}
                for ext in extensions
            ],
            "unique_folders": [
                {"folder": folder.folder_path, "count": folder.count}
                for folder in folders
            ]
        }

    except Exception as e:
        logger.error(f"Error getting file paths summary: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")