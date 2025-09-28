from app.core.database import SessionLocal
from app.models.file_path import FilePath
from app.models.user import User
from pathlib import Path
from datetime import datetime
import os

session = SessionLocal()
try:
    # Obter um usuário existente (admin)
    admin_user = session.query(User).filter(User.username == 'admin').first()
    if not admin_user:
        print("Usuário admin não encontrado!")
        exit(1)

    # Caminho completo do arquivo de exemplo
    example_file_path = r"C:\Users\formi\teste_gemini\dev\verificAI-code\codigo_analise.ts"

    # Verificar se o arquivo existe
    if not os.path.exists(example_file_path):
        print(f"Arquivo não encontrado: {example_file_path}")
        exit(1)

    # Verificar se já existe um file path para este arquivo
    existing_path = session.query(FilePath).filter(FilePath.full_path == example_file_path).first()
    if existing_path:
        print(f"File path já existe: {existing_path.full_path}")
        print(f"ID: {existing_path.id}, Usuário: {existing_path.user_id}")
    else:
        # Obter informações do arquivo
        file_stat = os.stat(example_file_path)
        file_path_obj = Path(example_file_path)

        # Criar novo file path com campos corretos
        new_file_path = FilePath(
            full_path=example_file_path,
            file_name="codigo_analise.ts",
            file_extension="ts",
            folder_path=str(file_path_obj.parent),
            file_size=file_stat.st_size,
            last_modified=datetime.fromtimestamp(file_stat.st_mtime),
            is_processed=True,
            processing_status="completed",
            user_id=admin_user.id,
            is_public=True,
            access_level="public",
            file_metadata={
                "language": "TypeScript",
                "framework": "React",
                "description": "Arquivo de exemplo para análise de código"
            }
        )

        session.add(new_file_path)
        session.commit()
        session.refresh(new_file_path)

        print(f"File path criado com sucesso:")
        print(f"ID: {new_file_path.id}")
        print(f"Caminho completo: {new_file_path.full_path}")
        print(f"Nome do arquivo: {new_file_path.file_name}")
        print(f"Extensão: {new_file_path.file_extension}")
        print(f"Tamanho: {new_file_path.get_human_readable_size()}")
        print(f"Usuário ID: {new_file_path.user_id}")
        print(f"Data criação: {new_file_path.created_at}")
        print(f"Processado: {new_file_path.is_processed}")
        print(f"Status: {new_file_path.processing_status}")

    # Listar todos os file paths disponíveis
    print("\nTodos os file paths cadastrados:")
    print("=" * 50)
    all_paths = session.query(FilePath).all()
    for path in all_paths:
        print(f"ID: {path.id}")
        print(f"Arquivo: {path.file_name}")
        print(f"Caminho: {path.full_path}")
        print(f"Extensão: {path.file_extension}")
        print(f"Tamanho: {path.get_human_readable_size()}")
        print(f"Processado: {path.is_processed}")
        print(f"Status: {path.processing_status}")
        print("-" * 30)

finally:
    session.close()