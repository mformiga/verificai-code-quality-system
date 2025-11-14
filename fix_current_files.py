#!/usr/bin/env python3
"""
Script to copy existing registered files to uploads folder
"""

import sys
import os
import shutil
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

os.chdir(Path(__file__).parent / "backend")

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.file_path import FilePath

def fix_current_files():
    """
    Copy files from their registered absolute paths to uploads folder and update database
    """
    db = SessionLocal()
    uploads_path = Path("uploads")
    uploads_path.mkdir(exist_ok=True)

    try:
        files = db.query(FilePath).all()
        print(f"Found {len(files)} files in database")

        copied_count = 0
        updated_count = 0
        error_count = 0

        for file in files:
            print(f"\nProcessing: {file.file_name}")
            print(f"  Current path: {file.full_path}")
            print(f"  Access level: {file.access_level}")

            # Check if source file exists
            source_path = Path(file.full_path)
            if not source_path.exists():
                print(f"  ERROR: Source file not found")
                error_count += 1
                continue

            # Create destination path in uploads
            dest_path = uploads_path / file.file_name
            print(f"  Destination: {dest_path}")

            # Copy file to uploads if needed
            if not dest_path.exists() or dest_path.stat().st_size != source_path.stat().st_size:
                try:
                    shutil.copy2(source_path, dest_path)
                    print(f"  COPIED: {source_path} -> {dest_path}")
                    copied_count += 1
                except Exception as e:
                    print(f"  ERROR copying file: {e}")
                    error_count += 1
                    continue
            else:
                print(f"  SKIPPED: File already exists")

            # Update database record with relative path and read access
            file.full_path = str(dest_path)
            file.folder_path = "uploads"
            file.access_level = "read"
            updated_count += 1
            print(f"  UPDATED: Database path to '{file.full_path}', access to 'read'")

        db.commit()

        print(f"\n=== SUMMARY ===")
        print(f"Total files: {len(files)}")
        print(f"Files copied: {copied_count}")
        print(f"Database updated: {updated_count}")
        print(f"Errors: {error_count}")

        return copied_count > 0

    except Exception as e:
        print(f"ERROR: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("Fixing current files...")
    success = fix_current_files()

    if success:
        print("\nSUCCESS: Files fixed and ready for analysis!")
    else:
        print("\nERROR: Failed to fix files")