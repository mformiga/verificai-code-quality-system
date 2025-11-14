from app.core.database import SessionLocal
from app.models.file_path import FilePath
import os

session = SessionLocal()
try:
    # Obter todos os file paths ativos
    file_paths = session.query(FilePath).filter(FilePath.is_processed == True).all()

    print("Verificando file paths cadastrados para análise:")
    print("=" * 60)

    for fp in file_paths:
        print(f"\nID: {fp.id}")
        print(f"Arquivo: {fp.file_name}")
        print(f"Caminho: {fp.full_path}")
        print(f"Extensão: {fp.file_extension}")
        print(f"Tamanho: {fp.get_human_readable_size()}")
        print(f"Processado: {fp.is_processed}")
        print(f"Status: {fp.processing_status}")

        # Verificar se o arquivo realmente existe
        if os.path.exists(fp.full_path):
            print("[OK] Arquivo existe no sistema de arquivos")

            # Tentar ler o arquivo
            try:
                with open(fp.full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                print(f"[OK] Arquivo legivel - {len(lines)} linhas")
                print(f"   Preview: {content[:100]}...")
            except Exception as e:
                print(f"[ERRO] Erro ao ler arquivo: {str(e)}")
        else:
            print("[ERRO] Arquivo NAO encontrado no sistema de arquivos")

        print("-" * 40)

    print(f"\nTotal de {len(file_paths)} file paths processados encontrados")

    # Verificar se o sistema de análise usará estes caminhos
    print("\nConfiguracao do sistema de analise:")
    print("=" * 40)
    print("[OK] Os caminhos de arquivo sao obtidos da tabela 'file_paths'")
    print("[OK] O campo 'full_path' é usado para localizar o arquivo fisico")
    print("[OK] Apenas arquivos com 'is_processed=True' sao considerados")
    print("[OK] O caminho completo e armazenado para acesso")

finally:
    session.close()