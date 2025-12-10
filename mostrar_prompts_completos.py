#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import psycopg2
from dotenv import load_dotenv

# Carregar variáveis de ambiente
if os.path.exists('.env.local'):
    load_dotenv('.env.local')
if os.path.exists('.env.supabase_local'):
    load_dotenv('.env.supabase_local')

POSTGRES_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': os.getenv('POSTGRES_PORT', '5432'),
    'database': os.getenv('POSTGRES_DB', 'verificai'),
    'user': os.getenv('POSTGRES_USER', 'verificai'),
    'password': os.getenv('POSTGRES_PASSWORD', 'verificai123')
}

def mostrar_prompts_completos():
    print("=== CONTEUDO COMPLETO DAS TABELAS DE PROMPTS - POSTGRESQL LOCAL ===\n")

    try:
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        cursor = conn.cursor()

        # 1. Tabela prompts
        print("TABELA: prompts")
        print("=" * 80)
        cursor.execute("""
            SELECT id, user_id, type, content, version, created_at, updated_at, created_by, updated_by
            FROM prompts
            ORDER BY id
        """)
        prompts = cursor.fetchall()

        if prompts:
            for prompt in prompts:
                print(f"\nID: {prompt[0]}")
                print(f"   User ID: {prompt[1]}")
                print(f"   Type: {prompt[2]}")
                print(f"   Version: {prompt[4]}")
                print(f"   Created: {prompt[5]}")
                print(f"   Updated: {prompt[6]}")
                print(f"   Created By: {prompt[7]}")
                print(f"   Updated By: {prompt[8]}")
                print(f"   Content:")
                content_lines = prompt[3].split('\n')
                for line in content_lines[:50]:  # Limitar primeiras 50 linhas
                    print(f"     {line}")
                if len(content_lines) > 50:
                    print(f"     ... (mais {len(content_lines) - 50} linhas)")
                print("-" * 80)
        else:
            print("   Nenhum prompt encontrado na tabela prompts")

        print(f"\nTotal de prompts: {len(prompts)}\n")

        # 2. Tabela prompt_configurations
        print("\nTABELA: prompt_configurations")
        print("=" * 80)
        cursor.execute("""
            SELECT id, user_id, prompt_type, name, description, content, is_active, is_default, settings, created_at, updated_at, created_by, updated_by
            FROM prompt_configurations
            ORDER BY id
        """)
        configurations = cursor.fetchall()

        if configurations:
            for config in configurations:
                print(f"\nID: {config[0]}")
                print(f"   User ID: {config[1]}")
                print(f"   Prompt Type: {config[2]}")
                print(f"   Name: {config[3]}")
                print(f"   Description: {config[4]}")
                print(f"   Is Active: {config[6]}")
                print(f"   Is Default: {config[7]}")
                print(f"   Settings: {config[8]}")
                print(f"   Created: {config[9]}")
                print(f"   Updated: {config[10]}")
                print(f"   Created By: {config[11]}")
                print(f"   Updated By: {config[12]}")
                print(f"   Content:")
                content_lines = config[5].split('\n')
                for line in content_lines[:30]:  # Limitar primeiras 30 linhas
                    print(f"     {line}")
                if len(content_lines) > 30:
                    print(f"     ... (mais {len(content_lines) - 30} linhas)")
                print("-" * 80)
        else:
            print("   Nenhuma configuracao encontrada na tabela prompt_configurations")

        print(f"\nTotal de configuracoes: {len(configurations)}\n")

        # 3. Tabela prompt_history
        print("\nTABELA: prompt_history")
        print("=" * 80)
        cursor.execute("""
            SELECT id, prompt_id, version, content, created_at, updated_at
            FROM prompt_history
            ORDER BY id DESC
        """)
        history = cursor.fetchall()

        if history:
            for hist in history:
                print(f"\nID: {hist[0]}")
                print(f"   Prompt ID: {hist[1]}")
                print(f"   Version: {hist[2]}")
                print(f"   Created: {hist[4]}")
                print(f"   Updated: {hist[5]}")
                print(f"   Content:")
                content_lines = hist[3].split('\n')
                for line in content_lines[:20]:  # Limitar primeiras 20 linhas
                    print(f"     {line}")
                if len(content_lines) > 20:
                    print(f"     ... (mais {len(content_lines) - 20} linhas)")
                print("-" * 80)
        else:
            print("   Nenhum historico encontrado na tabela prompt_history")

        print(f"\nTotal de historico: {len(history)}")

        # Resumo geral
        print("\n" + "=" * 80)
        print("RESUMO GERAL")
        print("=" * 80)
        print(f"Prompts ativos: {len(prompts)}")
        print(f"Configuracoes: {len(configurations)}")
        print(f"Historico: {len(history)}")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"ERRO: {str(e)}")

if __name__ == "__main__":
    mostrar_prompts_completos()