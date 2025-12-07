#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Listar todas as tabelas no schema public do Supabase
Projeto: jjxmfidggofuaxcdtkrd
"""

import os
import sys
from supabase import create_client
import requests
import json

# Configura UTF-8 para output
if sys.platform == "win32":
    os.system('chcp 65001 >nul')

def load_supabase_config():
    """Carrega configuracao do Supabase"""
    env_file = ".env.supabase"

    if not os.path.exists(env_file):
        print(f"ERRO: Arquivo {env_file} nao encontrado")
        return None

    with open(env_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    config = {}
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            key, value = line.split('=', 1)
            config[key] = value

    return config

def list_all_tables():
    """Lista todas as tabelas usando SQL direto via REST API"""

    config = load_supabase_config()
    if not config:
        return False

    # Headers para autenticacao
    headers = {
        'apikey': config['SUPABASE_SERVICE_ROLE_KEY'],
        'Authorization': f'Bearer {config["SUPABASE_SERVICE_ROLE_KEY"]}',
        'Content-Type': 'application/json',
        'Prefer': 'return=minimal'
    }

    # SQL para listar todas as tabelas
    sql_query = """
    SELECT
        t.table_name,
        t.table_type,
        obj_description(c.oid) as table_comment,
        pg_size_pretty(pg_total_relation_size(c.oid)) as size
    FROM information_schema.tables t
    LEFT JOIN pg_class c ON c.relname = t.table_name
    LEFT JOIN pg_namespace n ON n.oid = c.relnamespace AND n.nspname = t.table_schema
    WHERE t.table_schema = 'public'
    AND t.table_type = 'BASE TABLE'
    ORDER BY t.table_name;
    """

    # Executa SQL via REST API do Supabase
    url = f"{config['SUPABASE_URL']}/rest/v1/rpc/sql"

    payload = {
        "query": sql_query
    }

    try:
        print("[INFO] Listando todas as tabelas do schema public...")
        print("=" * 60)

        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            tables = response.json()

            if tables:
                print(f"\n[INFO] Encontradas {len(tables)} tabelas:")
                print("-" * 60)

                for table in tables:
                    print(f"\n  Tabela: {table['table_name']}")
                    print(f"    Tipo: {table['table_type']}")
                    print(f"    Tamanho: {table['size']}")
                    if table['table_comment']:
                        print(f"    Descricao: {table['table_comment']}")

                # Lista resumida
                print("\n\n[SUMMARY] Lista completa de tabelas:")
                print("-" * 60)
                for table in tables:
                    print(f"  - {table['table_name']}")

                return tables
            else:
                print("[INFO] Nenhuma tabela encontrada no schema public")
                return []

        else:
            print(f"[ERRO] Falha na consulta SQL: {response.status_code}")
            print(f"Response: {response.text}")
            return None

    except Exception as e:
        print(f"[ERRO] Erro ao listar tabelas: {e}")
        return None

def get_table_structure(table_name, config):
    """Obtem a estrutura detalhada de uma tabela"""

    headers = {
        'apikey': config['SUPABASE_SERVICE_ROLE_KEY'],
        'Authorization': f'Bearer {config["SUPABASE_SERVICE_ROLE_KEY"]}',
        'Content-Type': 'application/json'
    }

    # SQL para obter estrutura da tabela
    sql_query = f"""
    SELECT
        c.column_name,
        c.data_type,
        c.is_nullable,
        c.column_default,
        c.character_maximum_length,
        c.numeric_precision,
        c.numeric_scale,
        CASE WHEN pk.column_name IS NOT NULL THEN 'YES' ELSE 'NO' END as is_primary_key
    FROM information_schema.columns c
    LEFT JOIN (
        SELECT ku.table_name, ku.column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage ku
            ON tc.constraint_name = ku.constraint_name
            AND tc.table_schema = ku.table_schema
        WHERE tc.constraint_type = 'PRIMARY KEY'
            AND tc.table_schema = 'public'
            AND tc.table_name = '{table_name}'
    ) pk ON c.column_name = pk.column_name
    WHERE c.table_schema = 'public'
        AND c.table_name = '{table_name}'
    ORDER BY c.ordinal_position;
    """

    url = f"{config['SUPABASE_URL']}/rest/v1/rpc/sql"
    payload = {"query": sql_query}

    try:
        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"[ERRO] Falha ao obter estrutura da tabela {table_name}: {response.status_code}")
            return None

    except Exception as e:
        print(f"[ERRO] Erro ao obter estrutura: {e}")
        return None

if __name__ == "__main__":
    print("\n[LISTA] Listagem completa de tabelas - Supabase")
    print("Projeto: jjxmfidggofuaxcdtkrd")
    print("=" * 60)

    # Listar todas as tabelas
    tables = list_all_tables()

    if tables:
        config = load_supabase_config()

        # Verificar estrutura das tabelas solicitadas
        print("\n\n[DETAIL] Estrutura das tabelas prompt_configurations e source_codes:")
        print("=" * 60)

        # Verificar prompt_configurations
        if any(t['table_name'] == 'prompt_configurations' for t in tables):
            print("\n[INFO] Estrutura da tabela prompt_configurations:")
            structure = get_table_structure('prompt_configurations', config)
            if structure:
                for col in structure:
                    null_str = "SIM" if col['is_nullable'] == 'YES' else "NAO"
                    pk_str = " (PK)" if col['is_primary_key'] == 'YES' else ""
                    print(f"  - {col['column_name']}{pk_str}")
                    print(f"    Tipo: {col['data_type']}")
                    if col['character_maximum_length']:
                        print(f"    Tamanho max: {col['character_maximum_length']}")
                    print(f"    Nulo: {null_str}")
                    if col['column_default']:
                        print(f"    Default: {col['column_default']}")
                    print()

        # Verificar se source_codes existe
        source_codes_exists = any(t['table_name'] == 'source_codes' for t in tables)
        if source_codes_exists:
            print("\n[INFO] Estrutura da tabela source_codes:")
            structure = get_table_structure('source_codes', config)
            if structure:
                for col in structure:
                    null_str = "SIM" if col['is_nullable'] == 'YES' else "NAO"
                    pk_str = " (PK)" if col['is_primary_key'] == 'YES' else ""
                    print(f"  - {col['column_name']}{pk_str}")
                    print(f"    Tipo: {col['data_type']}")
                    if col['character_maximum_length']:
                        print(f"    Tamanho max: {col['character_maximum_length']}")
                    print(f"    Nulo: {null_str}")
                    if col['column_default']:
                        print(f"    Default: {col['column_default']}")
                    print()
        else:
            print("\n[INFO] Tabela source_codes NAO existe no banco de dados")

    print("\n[OK] Listagem concluida!")