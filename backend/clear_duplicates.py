#!/usr/bin/env python3
"""
Script para limpar registros duplicados
"""

import sys
from pathlib import Path

# Add app directory to path
sys.path.append(str(Path(__file__).parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

def clear_duplicates():
    """Limpar todos os registros de arquivo para começar do zero"""

    print("=== Limpando Registros Duplicados ===")

    # Database connection
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        # Count before clearing
        from app.models.uploaded_file import UploadedFile
        from app.models.file_path import FilePath

        uploaded_count = db.query(UploadedFile).count()
        paths_count = db.query(FilePath).count()

        print(f"Registros atuais:")
        print(f"  - UploadedFiles: {uploaded_count}")
        print(f"  - FilePaths: {paths_count}")

        # Clear all records
        db.query(UploadedFile).delete()
        db.query(FilePath).delete()
        db.commit()

        print("OK: Todos os registros limpos")

        # Verify
        uploaded_after = db.query(UploadedFile).count()
        paths_after = db.query(FilePath).count()

        print(f"Registros após limpeza:")
        print(f"  - UploadedFiles: {uploaded_after}")
        print(f"  - FilePaths: {paths_after}")

    except Exception as e:
        print(f"Erro: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    clear_duplicates()