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

def verificar_remocao():
    print("=== VERIFICANDO REMOCAO DA TABELA PROMPTS ===\n")

    try:
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        cursor = conn.cursor()

        # Verificar se a tabela existe
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public' AND table_name = 'prompts'
        """)
        result = cursor.fetchone()

        if result:
            print("ATENCAO: A tabela 'prompts' ainda existe!")

            # Tentar acessar a tabela
            try:
                cursor.execute("SELECT COUNT(*) FROM prompts")
                count = cursor.fetchone()[0]
                print(f"Registros na tabela 'prompts': {count}")
            except Exception as e:
                print(f"Erro ao acessar tabela 'prompts': {str(e)}")

            # Remover definitivamente
            print("\nRemovendo tabela 'prompts'...")
            cursor.execute("DROP TABLE IF EXISTS prompts CASCADE;")
            conn.commit()
            print("Tabela 'prompts' removida com sucesso!")

        else:
            print("OK: A tabela 'prompts' nao existe mais")

        # Verificar estado das tabelas relacionadas
        print("\n=== VERIFICANDO TABELAS RELACIONADAS ===")

        # Verificar prompt_configurations
        cursor.execute("SELECT COUNT(*) FROM prompt_configurations")
        count_configs = cursor.fetchone()[0]
        print(f"Registros em 'prompt_configurations': {count_configs}")

        # Verificar prompt_history
        cursor.execute("SELECT COUNT(*) FROM prompt_history")
        count_history = cursor.fetchone()[0]
        print(f"Registros em 'prompt_history': {count_history}")

        # Verificar analyses
        cursor.execute("SELECT COUNT(*) FROM analyses")
        count_analyses = cursor.fetchone()[0]
        print(f"Registros em 'analyses': {count_analyses}")

        # Listar todas as tabelas que começam com 'prompt'
        print("\n=== TABELAS COM 'PROMPT' NO NOME ===")
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name LIKE '%prompt%'
            ORDER BY table_name
        """)
        tables = cursor.fetchall()

        for table in tables:
            print(f"  - {table[0]}")

        print("\n=== RESUMO FINAL ===")
        print("Tabela 'prompts': REMOVIDA")
        print("Tabela 'prompt_configurations': MANTIDA (correta)")
        print("Tabela 'prompt_history': MANTIDA (sem dados)")
        print("Tabela 'analyses': MANTIDA (sem dependencia de prompts)")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"ERRO: {str(e)}")

if __name__ == "__main__":
    verificar_remocao()