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

def mostrar_prompts_locais():
    print("=== CONTEUDO DAS ABAS DE PROMPTS - POSTGRESQL LOCAL ===\n")

    try:
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        cursor = conn.cursor()

        # 1. Tabela prompts
        print("TABELA: prompts")
        print("=" * 60)
        cursor.execute("""
            SELECT id, name, content, created_at, updated_at
            FROM prompts
            ORDER BY id
        """)
        prompts = cursor.fetchall()

        if prompts:
            for prompt in prompts:
                print(f"\nID: {prompt[0]}")
                print(f"   Nome: {prompt[1]}")
                print(f"   Conteudo: {prompt[2][:200]}{'...' if len(prompt[2]) > 200 else ''}")
                print(f"   Criado: {prompt[3]}")
                print(f"   Atualizado: {prompt[4]}")
                print("-" * 40)
        else:
            print("   Nenhum prompt encontrado na tabela prompts")

        print(f"\nTotal de prompts: {len(prompts)}\n")

        # 2. Tabela prompt_configurations
        print("\nTABELA: prompt_configurations")
        print("=" * 60)
        cursor.execute("""
            SELECT id, prompt_id, configuration_type, configuration_data, created_at, updated_at
            FROM prompt_configurations
            ORDER BY id
        """)
        configurations = cursor.fetchall()

        if configurations:
            for config in configurations:
                print(f"\nID: {config[0]}")
                print(f"   Prompt ID: {config[1]}")
                print(f"   Tipo: {config[2]}")
                print(f"   Config: {config[3]}")
                print(f"   Criado: {config[4]}")
                print(f"   Atualizado: {config[5]}")
                print("-" * 40)
        else:
            print("   Nenhuma configuracao encontrada na tabela prompt_configurations")

        print(f"\nTotal de configuracoes: {len(configurations)}\n")

        # 3. Tabela prompt_history
        print("\nTABELA: prompt_history")
        print("=" * 60)
        cursor.execute("""
            SELECT id, prompt_id, version, content, change_description, created_by, created_at
            FROM prompt_history
            ORDER BY id DESC
            LIMIT 10
        """)
        history = cursor.fetchall()

        if history:
            for hist in history:
                print(f"\nID: {hist[0]}")
                print(f"   Prompt ID: {hist[1]}")
                print(f"   Versao: {hist[2]}")
                print(f"   Descricao: {hist[4]}")
                print(f"   Criado por: {hist[5]}")
                print(f"   Data: {hist[6]}")
                print(f"   Conteudo: {hist[3][:300]}{'...' if len(hist[3]) > 300 else ''}")
                print("-" * 40)
        else:
            print("   Nenhum historico encontrado na tabela prompt_history")

        print(f"\nTotal de historico (ultimos 10): {len(history)}")

        # Resumo geral
        print("\n" + "=" * 60)
        print("RESUMO GERAL")
        print("=" * 60)
        print(f"Prompts ativos: {len(prompts)}")
        print(f"Configuracoes: {len(configurations)}")
        print(f"Historico (ultimos 10): {len(history)}")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"ERRO: {str(e)}")

if __name__ == "__main__":
    mostrar_prompts_locais()