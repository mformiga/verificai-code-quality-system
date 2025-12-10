#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para mostrar o conteúdo detalhado dos prompts da tabela prompt_configurations
"""

import psycopg2
import os
import sys
from dotenv import load_dotenv

# Configurar encoding para Windows
if sys.platform == 'win32':
    os.system('chcp 65001 > nul')

# Carregar variáveis de ambiente
load_dotenv('.env.local')
load_dotenv('.env')

# Configuração do banco PostgreSQL
POSTGRES_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': os.getenv('POSTGRES_PORT', '5432'),
    'database': os.getenv('POSTGRES_DB', 'verificai'),
    'user': os.getenv('POSTGRES_USER', 'verificai'),
    'password': os.getenv('POSTGRES_PASSWORD', 'verificai123')
}

def format_content(content, max_length=200):
    """Formata o conteúdo para exibição"""
    if content is None:
        return "NULL"
    if len(content) <= max_length:
        return content
    return content[:max_length] + "..."

def show_prompts_detail():
    try:
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        cursor = conn.cursor()

        # Consultar prompts ordenados por tipo e data de atualização
        cursor.execute("""
            SELECT id, user_id, prompt_type, name, description, content,
                   is_active, is_default, created_at, updated_at
            FROM prompt_configurations
            ORDER BY prompt_type, updated_at DESC;
        """)

        rows = cursor.fetchall()

        print("=" * 80)
        print("CONTEÚDO DETALHADO DA TABELA PROMPT_CONFIGURATIONS")
        print("=" * 80)
        print(f"Total de prompts encontrados: {len(rows)}")
        print()

        current_prompt_type = None
        for i, row in enumerate(rows, 1):
            (prompt_id, user_id, prompt_type, name, description,
             content, is_active, is_default, created_at, updated_at) = row

            if prompt_type != current_prompt_type:
                if current_prompt_type is not None:
                    print("\n" + "-" * 60)
                current_prompt_type = prompt_type
                print(f"[TIPO]: {prompt_type}")
                print("=" * 60)

            print(f"\n[PROMPT #{i}]")
            print(f"   ID: {prompt_id}")
            print(f"   User ID: {user_id}")
            print(f"   Nome: {name}")
            print(f"   Descrição: {description}")
            print(f"   Ativo: {'[SIM]' if is_active else '[NAO]'}")
            print(f"   Padrão: {'[SIM]' if is_default else '[NAO]'}")
            print(f"   Criado: {created_at}")
            print(f"   Atualizado: {updated_at}")

            print(f"\n[CONTEUDO]:")
            print("-" * 40)
            # Mostrar o conteúdo completo, mas formatado
            print(content)
            print("-" * 40)

        print("\n" + "=" * 80)
        print("RESUMO POR TIPO DE PROMPT")
        print("=" * 80)

        # Agrupar por tipo
        cursor.execute("""
            SELECT prompt_type, COUNT(*) as total,
                   COUNT(CASE WHEN is_active = true THEN 1 END) as active
            FROM prompt_configurations
            GROUP BY prompt_type
            ORDER BY prompt_type;
        """)

        summary = cursor.fetchall()
        for prompt_type, total, active in summary:
            print(f"  {prompt_type}: {total} prompts ({active} ativos)")

        cursor.close()
        conn.close()
        print("\n[OK] Consulta concluída com sucesso!")

    except Exception as e:
        print(f"[ERRO] {e}")

if __name__ == "__main__":
    show_prompts_detail()