#!/usr/bin/env python3
"""
Script para limpar arquivos duplicados no banco de dados
"""

from app.core.database import SessionLocal
from app.models.uploaded_file import UploadedFile
from collections import defaultdict

def clear_duplicates():
    """Remover arquivos duplicados, mantendo apenas o mais recente"""
    session = SessionLocal()

    try:
        # Buscar todos os arquivos
        all_files = session.query(UploadedFile).all()

        # Agrupar por nome de arquivo
        file_groups = defaultdict(list)
        for file in all_files:
            file_groups[file.full_path].append(file)

        duplicates_count = 0
        kept_count = 0

        # Para cada grupo de arquivos com o mesmo nome
        for file_name, files in file_groups.items():
            if len(files) > 1:
                print(f"\nArquivo duplicado: {file_name}")
                print(f"  Encontrados: {len(files)} cópias")

                # Ordenar por ID (o mais recente terá maior ID)
                files.sort(key=lambda x: x.id)

                # Manter o mais recente (último ID)
                keep_file = files[-1]
                files_to_remove = files[:-1]

                print(f"  Mantendo: ID {keep_file.id} ({keep_file.file_id})")
                print(f"  Removendo: {[f\"ID {f.id} ({f.file_id})\" for f in files_to_remove]}")

                # Remover os duplicados
                for file_to_remove in files_to_remove:
                    session.delete(file_to_remove)
                    duplicates_count += 1

                kept_count += 1
            else:
                kept_count += 1

        # Commit das alterações
        session.commit()

        print(f"\n=== Resumo ===")
        print(f"Arquivos únicos mantidos: {kept_count}")
        print(f"Duplicados removidos: {duplicates_count}")
        print(f"Total de arquivos antes: {len(all_files)}")
        print(f"Total de arquivos depois: {len(all_files) - duplicates_count}")

    except Exception as e:
        print(f"Erro ao limpar duplicados: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    clear_duplicates()
