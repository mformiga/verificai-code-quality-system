#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Status completo das tabelas no Supabase
Projeto: jjxmfidggofuaxcdtkrd
"""

import os
from supabase import create_client
import json

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

def check_all_tables():
    """Verifica todas as tabelas conhecidas"""

    config = load_supabase_config()
    if not config:
        return False

    try:
        client = create_client(config['SUPABASE_URL'], config['SUPABASE_SERVICE_ROLE_KEY'])
        print("Conectado ao Supabase - Projeto:", config['SUPABASE_PROJECT_REF'])
        print("=" * 70)

        # Lista completa de tabelas para verificar
        tables_to_check = [
            # Tabelas de autenticacao/perfil
            'users',
            'profiles',
            'auth.users',
            'auth.sessions',

            # Tabelas do sistema AVALIA
            'prompt_configurations',
            'source_codes',
            'file_paths',
            'files',
            'uploads',
            'documents',

            # Tabelas de analise
            'analysis_results',
            'analyses',
            'code_analysis',

            # Outras tabelas possiveis
            'projects',
            'user_files',
            'api_keys',
            'settings',
            'notifications',
            'logs',
            'audit_log',
            'comments',
            'tags',
            'categories',

            # Tabelas de sistema Supabase
            'schema_migrations',
            'extensions',
            'pg_stat_statements'
        ]

        print("\nVERIFICACAO DE TABELAS:")
        print("-" * 70)

        found_tables = []
        not_found = []

        for table in tables_to_check:
            try:
                # Para tabelas auth, precisamos de abordagem diferente
                if table.startswith('auth.'):
                    # Tenta via RPC se existir, senao pula
                    print(f"{'-':<3} {table:<35} [SKIP] Tabela de sistema auth")
                    continue

                # Tenta fazer SELECT COUNT na tabela
                response = client.table(table).select('count', count='exact').limit(1).execute()

                if response.data is not None:
                    count = response.count if hasattr(response, 'count') else 0
                    found_tables.append((table, count))
                    print(f"[OK] {table:<35} {count:>6} registros")
                else:
                    not_found.append(table)
                    print(f"[X]  {table:<35} NAO encontrada")

            except Exception as e:
                not_found.append(table)
                error_msg = str(e)[:50]
                print(f"[X]  {table:<35} Erro: {error_msg}...")

        # Resumo
        print("\n" + "=" * 70)
        print("RESUMO DO STATUS DAS TABELAS:")
        print("=" * 70)

        print(f"\nTabelas encontradas: {len(found_tables)}/{len(tables_to_check)}")
        if found_tables:
            print("\nTABELAS EXISTENTES:")
            print("-" * 50)
            for table, count in sorted(found_tables):
                print(f"  {table:<35} - {count} registros")

        print(f"\nTabelas nao encontradas: {len(not_found)}")
        if not_found:
            print("\nTABELAS INEXISTENTES:")
            print("-" * 50)
            for table in sorted(not_found):
                print(f"  - {table}")

        # Verificacao especifica
        print("\n" + "=" * 70)
        print("VERIFICACAO DAS TABELAS SOLICITADAS:")
        print("=" * 70)

        prompt_configs_found = any(t[0] == 'prompt_configurations' for t in found_tables)
        source_codes_found = any(t[0] == 'source_codes' for t in found_tables)

        print(f"\n1. prompt_configurations:")
        print(f"   Status: {'EXISTE' if prompt_configs_found else 'NAO EXISTE'}")
        if prompt_configs_found:
            count = next((c for t, c in found_tables if t == 'prompt_configurations'), 0)
            print(f"   Registros: {count}")

            # Tenta obter detalhes
            try:
                response = client.table('prompt_configurations').select('*').limit(3).execute()
                if response.data:
                    print("   Estrutura (colunas):")
                    if response.data:
                        columns = list(response.data[0].keys())
                        for col in sorted(columns):
                            print(f"     - {col}")
            except:
                pass

        print(f"\n2. source_codes:")
        print(f"   Status: {'EXISTE' if source_codes_found else 'NAO EXISTE'}")
        if source_codes_found:
            count = next((c for t, c in found_tables if t == 'source_codes'), 0)
            print(f"   Registros: {count}")
        else:
            print("   >>> TABELA NECESSARIA NAO CRIADA AINDA <<<")

        # Outras tabelas importantes
        print("\n3. Outras tabelas importantes:")
        print("   - users:", "EXISTE" if any(t[0] == 'users' for t in found_tables) else "NAO EXISTE")
        print("   - profiles:", "EXISTE" if any(t[0] == 'profiles' for t in found_tables) else "NAO EXISTE")
        print("   - file_paths:", "EXISTE" if any(t[0] == 'file_paths' for t in found_tables) else "NAO EXISTE")

        print("\n" + "=" * 70)

        return True

    except Exception as e:
        print(f"\nERRO: Falha na conexao ou execucao: {e}")
        return False

if __name__ == "__main__":
    print("\nRELATORIO DE STATUS - SUPABASE")
    print("Projeto: jjxmfidggofuaxcdtkrd")
    print("=" * 70)

    success = check_all_tables()

    if success:
        print("\n[CONCLUIDO] Verificacao finalizada com sucesso!")
    else:
        print("\n[FALHA] Ocorreram erros durante a verificacao!")