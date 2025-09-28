#!/usr/bin/env python3
"""
Script para sincronizar arquivos físicos com o banco de dados
"""

import os
import sys
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add app directory to path
sys.path.append(str(Path(__file__).parent))

from app.core.database import get_db
from app.models.uploaded_file import UploadedFile, FileStatus, ProcessingStatus
from app.models.file_path import FilePath
from app.models.user import User
from app.core.config import settings

def sync_uploaded_files():
    """Sincronizar arquivos físicos com o banco de dados"""

    print("=== Sincronizando Arquivos Uploadados ===")

    # Database connection
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        # Get uploads directory
        uploads_dir = Path(__file__).parent / "uploads"
        if not uploads_dir.exists():
            print(f"Uploads directory not found: {uploads_dir}")
            return

        print(f"Scanning uploads directory: {uploads_dir}")

        # List physical files
        physical_files = list(uploads_dir.glob("file_*"))
        print(f"Found {len(physical_files)} physical files:")

        for file_path in physical_files:
            print(f"  - {file_path.name}")

        # Get user with ID 1 (assume it's the test user)
        test_user = db.query(User).filter(User.id == 1).first()
        if not test_user:
            print("Test user (ID=1) not found in database")
            return

        print(f"Using test user: {test_user.username} (ID: {test_user.id})")

        # Get existing uploaded files
        existing_uploaded = db.query(UploadedFile).filter(UploadedFile.user_id == test_user.id).all()
        print(f"Existing uploaded files in database: {len(existing_uploaded)}")

        # Process each physical file
        synced_count = 0
        for physical_file in physical_files:
            try:
                # Extract file info from filename
                filename = physical_file.name

                # Parse filename format: file_[uuid]_[original_name]
                if filename.startswith("file_") and "_" in filename:
                    parts = filename.split("_", 2)
                    if len(parts) >= 3:
                        file_uuid = parts[1]
                        original_name = parts[2]

                        # Check if already exists
                        existing = db.query(UploadedFile).filter(
                            UploadedFile.file_id == file_uuid
                        ).first()

                        if existing:
                            print(f"File already exists: {original_name}")
                            continue

                        # Create uploaded file record
                        file_size = physical_file.stat().st_size
                        file_extension = Path(original_name).suffix.lower().lstrip('.')

                        uploaded_file = UploadedFile(
                            file_id=file_uuid,
                            original_name=original_name,
                            file_path=str(physical_file),
                            relative_path=original_name,  # Simplified
                            file_size=file_size,
                            mime_type="application/octet-stream",
                            file_extension=file_extension,
                            storage_path=str(physical_file.absolute()),
                            status=FileStatus.COMPLETED,
                            upload_progress=100,
                            user_id=test_user.id,
                            is_processed=True,
                            processing_status=ProcessingStatus.COMPLETED
                        )

                        db.add(uploaded_file)

                        # Also create file_path record for display
                        file_path_record = FilePath(
                            file_id=f"path_{file_uuid}",
                            full_path=original_name,
                            file_name=original_name,
                            file_extension=file_extension,
                            folder_path="",
                            file_size=file_size,
                            is_processed=True,
                            user_id=test_user.id,
                            is_public=False,
                            access_level="private"
                        )

                        db.add(file_path_record)

                        print(f"OK: Created records for: {original_name}")
                        synced_count += 1

            except Exception as e:
                print(f"ERROR: Could not process {physical_file.name}: {e}")

        # Commit all changes
        db.commit()
        print(f"\n=== Sync Complete ===")
        print(f"Synced {synced_count} files to database")

        # Verify
        print(f"\n=== Verification ===")
        final_uploaded = db.query(UploadedFile).filter(UploadedFile.user_id == test_user.id).all()
        final_paths = db.query(FilePath).filter(FilePath.user_id == test_user.id).all()

        print(f"Uploaded files in database: {len(final_uploaded)}")
        print(f"File paths in database: {len(final_paths)}")

        for uploaded in final_uploaded:
            print(f"  - {uploaded.original_name} ({uploaded.file_id})")

    except Exception as e:
        print(f"Error during sync: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    sync_uploaded_files()