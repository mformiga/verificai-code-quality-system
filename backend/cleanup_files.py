#!/usr/bin/env python3
"""
Script para limpar arquivos que deveriam ter sido excluídos da IDE
"""

import sys
from pathlib import Path

# Add app directory to path
sys.path.append(str(Path(__file__).parent))

from app.core.database import SessionLocal
from app.models.uploaded_file import UploadedFile
from app.models.file_path import FilePath

def show_current_files():
    """Mostrar arquivos atuais no sistema"""
    db = SessionLocal()
    try:
        uploaded_files = db.query(UploadedFile).filter(UploadedFile.user_id == 1).all()
        file_paths = db.query(FilePath).filter(FilePath.user_id == 1).all()

        print("=== ARQUIVOS ATUAIS NO SISTEMA ===")
        print(f"UploadedFiles: {len(uploaded_files)}")
        print(f"FilePaths: {len(file_paths)}")

        print("\nUploadedFiles:")
        for uf in uploaded_files:
            print(f"  - {uf.original_name} (ID: {uf.file_id})")

        print("\nFilePaths:")
        for fp in file_paths:
            print(f"  - {fp.full_path} (ID: {fp.file_id})")

        print(f"\nArquivos físicos em uploads/:")
        uploads_dir = Path(__file__).parent / "uploads"
        physical_files = list(uploads_dir.glob("file_*"))
        print(f"Total: {len(physical_files)}")
        for pf in physical_files:
            print(f"  - {pf.name}")

    finally:
        db.close()

def delete_file_by_name(filename):
    """Excluir um arquivo pelo nome"""
    db = SessionLocal()
    try:
        print(f"\n=== EXCLUINDO ARQUIVO: {filename} ===")

        # Find in uploaded_files
        uploaded_file = db.query(UploadedFile).filter(
            UploadedFile.user_id == 1,
            (UploadedFile.original_name == filename) |
            (UploadedFile.relative_path == filename)
        ).first()

        if uploaded_file:
            print(f"Found UploadedFile: {uploaded_file.original_name}")

            # Delete physical file
            if Path(uploaded_file.storage_path).exists():
                Path(uploaded_file.storage_path).unlink()
                print(f"Physical file deleted: {uploaded_file.storage_path}")

            # Delete from file_paths
            file_path_record = db.query(FilePath).filter(
                FilePath.user_id == 1,
                (FilePath.full_path == uploaded_file.original_name) |
                (FilePath.full_path == uploaded_file.relative_path) |
                (FilePath.file_name == uploaded_file.original_name)
            ).first()

            if file_path_record:
                db.delete(file_path_record)
                print(f"FilePath record deleted")

            # Delete uploaded_file
            db.delete(uploaded_file)
            db.commit()
            print(f"UploadFile record deleted")

        else:
            print(f"Arquivo não encontrado no banco: {filename}")

    except Exception as e:
        print(f"Erro ao excluir arquivo: {e}")
        db.rollback()
    finally:
        db.close()

def main():
    """Função principal"""
    print("=== LIMPEZA DE ARQUIVOS ===")

    show_current_files()

    print(f"\n=== MENU ===")
    print("1. Mostrar arquivos atuais")
    print("2. Excluir arquivo específico")
    print("3. Sair")

    while True:
        choice = input("\nDigite sua opção (1-3): ").strip()

        if choice == "1":
            show_current_files()
        elif choice == "2":
            filename = input("Digite o nome do arquivo para excluir: ").strip()
            if filename:
                delete_file_by_name(filename)
                show_current_files()
        elif choice == "3":
            print("Saindo...")
            break
        else:
            print("Opção inválida!")

if __name__ == "__main__":
    main()