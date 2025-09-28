from app.core.database import SessionLocal
from app.models.uploaded_file import UploadedFile

session = SessionLocal()
try:
    files = session.query(UploadedFile).all()

    print("Arquivos cadastrados no banco para análise:")
    print("=" * 60)

    if not files:
        print("Nenhum arquivo encontrado no banco de dados.")
    else:
        for file in files:
            print(f"ID: {file.id}")
            print(f"File ID: {file.file_id}")
            print(f"Nome original: {file.original_name}")
            print(f"Caminho relativo: {file.file_path}")
            print(f"Caminho absoluto: {file.storage_path}")
            print(f"Caminho relativo original: {file.relative_path}")
            print(f"Tamanho: {file.file_size} bytes")
            print(f"Tipo MIME: {file.mime_type}")
            print(f"Extensão: {file.file_extension}")
            print(f"Status: {file.status}")
            print(f"Usuário ID: {file.user_id}")
            print(f"Data upload: {file.created_at}")
            print(f"Processado: {file.is_processed}")
            print("-" * 40)

    # Mostrar caminho completo que será usado na análise
    print("\nCaminhos completos para acesso aos arquivos:")
    print("=" * 60)
    for file in files:
        if file.storage_path:
            print(f"Arquivo: {file.original_name}")
            print(f"Path para análise: {file.storage_path}")
            print(f"Path relativo: {file.file_path}")
            print("-" * 30)
finally:
    session.close()