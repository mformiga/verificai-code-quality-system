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

def exportar_prompts_para_txt():
    print("Exportando prompts para arquivo prompts_locais.txt...")

    try:
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        cursor = conn.cursor()

        with open('prompts_locais.txt', 'w', encoding='utf-8') as f:
            f.write("=== CONTEUDO DAS ABAS DE PROMPTS - POSTGRESQL LOCAL ===\n\n")

            # 1. Tabela prompts
            f.write("TABELA: prompts\n")
            f.write("=" * 80 + "\n")
            cursor.execute("""
                SELECT id, user_id, type, content, version, created_at, updated_at, created_by, updated_by
                FROM prompts
                ORDER BY id
            """)
            prompts = cursor.fetchall()

            if prompts:
                for prompt in prompts:
                    f.write(f"\nID: {prompt[0]}\n")
                    f.write(f"User ID: {prompt[1]}\n")
                    f.write(f"Type: {prompt[2]}\n")
                    f.write(f"Version: {prompt[4]}\n")
                    f.write(f"Created: {prompt[5]}\n")
                    f.write(f"Updated: {prompt[6]}\n")
                    f.write(f"Created By: {prompt[7]}\n")
                    f.write(f"Updated By: {prompt[8]}\n")
                    f.write(f"Content:\n{prompt[3]}\n")
                    f.write("-" * 80 + "\n")
            else:
                f.write("Nenhum prompt encontrado na tabela prompts\n")

            f.write(f"\nTotal de prompts: {len(prompts)}\n\n")

            # 2. Tabela prompt_configurations
            f.write("\nTABELA: prompt_configurations\n")
            f.write("=" * 80 + "\n")
            cursor.execute("""
                SELECT id, user_id, prompt_type, name, description, content, is_active, is_default, settings, created_at, updated_at, created_by, updated_by
                FROM prompt_configurations
                ORDER BY id
            """)
            configurations = cursor.fetchall()

            if configurations:
                for config in configurations:
                    f.write(f"\nID: {config[0]}\n")
                    f.write(f"User ID: {config[1]}\n")
                    f.write(f"Prompt Type: {config[2]}\n")
                    f.write(f"Name: {config[3]}\n")
                    f.write(f"Description: {config[4]}\n")
                    f.write(f"Is Active: {config[6]}\n")
                    f.write(f"Is Default: {config[7]}\n")
                    f.write(f"Settings: {config[8]}\n")
                    f.write(f"Created: {config[9]}\n")
                    f.write(f"Updated: {config[10]}\n")
                    f.write(f"Created By: {config[11]}\n")
                    f.write(f"Updated By: {config[12]}\n")
                    f.write(f"Content:\n{config[5]}\n")
                    f.write("-" * 80 + "\n")
            else:
                f.write("Nenhuma configuracao encontrada na tabela prompt_configurations\n")

            f.write(f"\nTotal de configuracoes: {len(configurations)}\n\n")

            # 3. Tabela prompt_history
            f.write("\nTABELA: prompt_history\n")
            f.write("=" * 80 + "\n")
            cursor.execute("""
                SELECT id, prompt_id, version, content, created_at, updated_at
                FROM prompt_history
                ORDER BY id DESC
            """)
            history = cursor.fetchall()

            if history:
                for hist in history:
                    f.write(f"\nID: {hist[0]}\n")
                    f.write(f"Prompt ID: {hist[1]}\n")
                    f.write(f"Version: {hist[2]}\n")
                    f.write(f"Created: {hist[4]}\n")
                    f.write(f"Updated: {hist[5]}\n")
                    f.write(f"Content:\n{hist[3]}\n")
                    f.write("-" * 80 + "\n")
            else:
                f.write("Nenhum historico encontrado na tabela prompt_history\n")

            f.write(f"\nTotal de historico: {len(history)}\n")

            # Resumo geral
            f.write("\n" + "=" * 80 + "\n")
            f.write("RESUMO GERAL\n")
            f.write("=" * 80 + "\n")
            f.write(f"Prompts ativos: {len(prompts)}\n")
            f.write(f"Configuracoes: {len(configurations)}\n")
            f.write(f"Historico: {len(history)}\n")

        cursor.close()
        conn.close()

        print("Arquivo 'prompts_locais.txt' criado com sucesso!")
        print(f"Conteúdo exportado:")
        print(f"  - {len(prompts)} prompts na tabela prompts")
        print(f"  - {len(configurations)} configuracoes na tabela prompt_configurations")
        print(f"  - {len(history)} registros na tabela prompt_history")

    except Exception as e:
        print(f"ERRO: {str(e)}")

if __name__ == "__main__":
    exportar_prompts_para_txt()