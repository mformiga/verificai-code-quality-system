#!/usr/bin/env python3
"""
Script para mostrar o último prompt enviado para a LLM
"""

import sys
from pathlib import Path

# Add app directory to path
sys.path.append(str(Path(__file__).parent))

def show_latest_prompt():
    """Mostrar o conteúdo do último prompt enviado para a LLM"""

    prompts_dir = Path(__file__).parent / "prompts"
    latest_prompt_path = prompts_dir / "latest_prompt.txt"

    if not latest_prompt_path.exists():
        print("Nenhum prompt encontrado.")
        print("Execute uma análise primeiro para gerar um prompt.")
        return

    try:
        with open(latest_prompt_path, "r", encoding="utf-8") as f:
            content = f.read()

        print("="*80)
        print("ÚLTIMO PROMPT ENVIADO PARA A LLM")
        print("="*80)
        print(content)

        # Mostrar informações do arquivo
        print("\n" + "="*80)
        print("INFORMAÇÕES DO ARQUIVO")
        print("="*80)
        print(f"Path: {latest_prompt_path}")
        print(f"Tamanho: {len(content)} caracteres")
        print(f"Linhas: {len(content.splitlines())}")

        # Listar todos os prompts gravados
        print(f"\n" + "="*80)
        print("TODOS OS PROMPTS SALVOS")
        print("="*80)
        prompt_files = list(prompts_dir.glob("prompt_llm_*.txt"))
        prompt_files.sort(reverse=True)  # Mais recentes primeiro

        if prompt_files:
            print(f"Total de prompts salvos: {len(prompt_files)}")
            for i, prompt_file in enumerate(prompt_files[:10]):  # Mostrar os 10 mais recentes
                stat = prompt_file.stat()
                print(f"  {i+1}. {prompt_file.name} - {stat.st_size} bytes - {Path(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print("Nenhum prompt adicional encontrado.")

    except Exception as e:
        print(f"Erro ao ler o prompt: {e}")

if __name__ == "__main__":
    show_latest_prompt()