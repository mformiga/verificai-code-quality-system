#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificacao de tabelas no Supabase
Projeto: jjxmfidggofuaxcdtkrd
"""

import os
import sys
from supabase import create_client

# Configura UTF-8 para output
if sys.platform == "win32":
    os.system('chcp 65001 >nul')

def load_supabase_config():
    """Carrega configuracao do Supabase"""
    # Lê do arquivo .env.supabase
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

def check_tables():
    """Verifica tabelas no Supabase"""

    # Carregar configuracao
    config = load_supabase_config()
    if not config:
        return False

    # Criar cliente Supabase
    try:
        client = create_client(config['SUPABASE_URL'], config['SUPABASE_SERVICE_ROLE_KEY'])
        print("[OK] Conectado ao Supabase")
        print(f"   Projeto: {config['SUPABASE_PROJECT_REF']}")
        print(f"   URL: {config['SUPABASE_URL']}")
        print()
    except Exception as e:
        print(f"[ERRO] Erro ao conectar ao Supabase: {e}")
        return False

    try:
        # Lista de tabelas para verificar
        tables_to_check = [
            'prompt_configurations',
            'source_codes',
            'profiles',
            'users',
            'file_paths',
            'files',
            'uploads',
            'documents',
            'analysis_results',
            'analyses',
            'code_analysis'
        ]

        print("\n[INFO] Verificando tabelas no schema public:")
        print("=" * 50)

        found_tables = []
        for table in tables_to_check:
            try:
                # Tenta fazer um SELECT COUNT na tabela
                response = client.table(table).select('count', count='exact').limit(1).execute()

                if hasattr(response, 'data') and response.data is not None:
                    count = response.count if hasattr(response, 'count') else 0
                    found_tables.append((table, count))
                    print(f"[OK] {table}: {count} registros")
                else:
                    print(f"[FAIL] {table}: Nao encontrada")
            except Exception as e:
                print(f"[FAIL] {table}: Erro - {str(e)[:50]}...")

        # 2. Verificar estrutura das tabelas encontradas
        print("\n[INFO] Estrutura das tabelas encontradas:")
        print("=" * 50)

        for table_name, count in found_tables:
            print(f"\n[INFO] Tabela: {table_name}")
            print(f"   Registros: {count}")

            # Tenta obter a estrutura da tabela
            try:
                # Pega alguns registros para inferir a estrutura
                response = client.table(table_name).select('*').limit(1).execute()

                if response.data:
                    columns = list(response.data[0].keys()) if response.data[0] else []
                    print("   Colunas:")
                    for col in columns:
                        print(f"     - {col}")
                else:
                    print("   (Tabela vazia)")
            except Exception as e:
                print(f"   Erro ao obter estrutura: {str(e)[:50]}...")

        # 3. Resumo
        print("\n[SUMMARY] Resumo:")
        print("=" * 50)
        print(f"Total de tabelas verificadas: {len(tables_to_check)}")
        print(f"Tabelas encontradas: {len(found_tables)}")

        if found_tables:
            print("\nTabelas existentes:")
            for table_name, count in found_tables:
                print(f"  OK {table_name} ({count} registros)")

        # Verificacao especifica para as tabelas solicitadas
        print("\n[CHECK] Verificacao das tabelas solicitadas:")
        print("=" * 50)

        prompt_configs_found = any(t[0] == 'prompt_configurations' for t in found_tables)
        source_codes_found = any(t[0] == 'source_codes' for t in found_tables)

        print(f"prompt_configurations: {'EXISTE' if prompt_configs_found else 'NAO ENCONTRADA'}")
        print(f"source_codes: {'EXISTE' if source_codes_found else 'NAO ENCONTRADA'}")

        return True

    except Exception as e:
        print(f"[ERRO] Erro durante a verificacao: {e}")
        return False

if __name__ == "__main__":
    print("\n[CHECK] Verificacao de tabelas - Supabase")
    print("Projeto: jjxmfidggofuaxcdtkrd")
    print("=" * 60)
    print()

    success = check_tables()

    if success:
        print("\n[OK] Verificacao concluida com sucesso!")
    else:
        print("\n[FAIL] Falha na verificacao!")
        sys.exit(1)