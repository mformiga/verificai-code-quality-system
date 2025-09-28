#!/usr/bin/env python3
"""
Teste para demonstrar o envio de múltiplos arquivos para a LLM
"""

import sys
from pathlib import Path

# Add app directory to path
sys.path.append(str(Path(__file__).parent))

from app.core.database import SessionLocal
from app.models.uploaded_file import UploadedFile
from app.models.file_path import FilePath

def test_multiple_files_analysis():
    """Testar como o sistema combina múltiplos arquivos para análise"""

    print("=== TESTE DE ANÁLISE COM MÚLTIPLOS ARQUIVOS ===")

    # Database connection
    db = SessionLocal()

    try:
        # Get all available files
        uploaded_files = db.query(UploadedFile).filter(UploadedFile.status == 'COMPLETED').all()

        print(f"Arquivos disponíveis: {len(uploaded_files)}")

        # Simulate file selection (like frontend would do)
        selected_files = uploaded_files[:3]  # Select first 3 files for demo

        print(f"\nArquivos selecionados para análise:")
        for i, uf in enumerate(selected_files):
            print(f"  {i+1}. {uf.original_name} ({uf.file_size} bytes)")
            print(f"     Path: {uf.file_path}")

        # Simulate the backend processing
        print(f"\n=== SIMULAÇÃO DE PROCESSAMENTO NO BACKEND ===")

        all_source_code = ""
        total_files_processed = 0

        for i, uploaded_file in enumerate(selected_files):
            try:
                # Read file content
                file_path = Path(uploaded_file.file_path)
                if file_path.exists():
                    with open(file_path, "r", encoding="utf-8") as f:
                        file_content = f.read()
                        file_size = len(file_content)

                    # Add file header and content (same logic as backend)
                    file_extension = uploaded_file.original_name.split('.')[-1] if '.' in uploaded_file.original_name else 'txt'
                    all_source_code += f"\n\n{'='*60}\n"
                    all_source_code += f"ARQUIVO: {uploaded_file.original_name}\n"
                    all_source_code += f"TAMANHO: {file_size} caracteres\n"
                    all_source_code += f"TIPO: {file_extension.upper()}\n"
                    all_source_code += f"{'='*60}\n\n"
                    all_source_code += file_content

                    total_files_processed += 1
                    print(f"OK: Arquivo {i+1} processado: {uploaded_file.original_name}")
                else:
                    print(f"ERRO: Arquivo nao encontrado: {uploaded_file.file_path}")

            except Exception as e:
                print(f"ERRO: Erro ao processar arquivo {uploaded_file.original_name}: {e}")

        print(f"\n=== RESUMO ===")
        print(f"Arquivos processados com sucesso: {total_files_processed}/{len(selected_files)}")
        print(f"Tamanho total do código combinado: {len(all_source_code)} caracteres")

        # Show sample of combined code
        print(f"\n=== EXEMPLO DO CÓDIGO COMBINADO (primeiros 500 caracteres) ===")
        sample = all_source_code[:500] + "..." if len(all_source_code) > 500 else all_source_code
        print(sample)

        print(f"\n=== EXEMPLO DO FINAL DO CÓDIGO COMBINADO (últimos 300 caracteres) ===")
        sample_end = all_source_code[-300:] if len(all_source_code) > 300 else all_source_code
        print(sample_end)

        print(f"\nOK: O SISTEMA ESTA PRONTO PARA ENVIAR TODOS OS {total_files_processed} ARQUIVOS PARA A LLM!")

    except Exception as e:
        print(f"Erro durante teste: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_multiple_files_analysis()