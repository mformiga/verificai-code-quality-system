#!/usr/bin/env python3
"""
Script para verificar a tabela source_codes no Supabase
"""

import os
import json
from dotenv import load_dotenv
import requests
import sys

# Carregar variáveis de ambiente
load_dotenv('.env.supabase')

# Configurações do Supabase
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    print("[!] Erro: Variáveis de ambiente do Supabase não encontradas")
    sys.exit(1)

# Headers para autenticação
headers = {
    'apikey': SUPABASE_SERVICE_ROLE_KEY,
    'Authorization': f'Bearer {SUPABASE_SERVICE_ROLE_KEY}',
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

print("[*] Verificando tabela source_codes no Supabase...")
print("=" * 60)

# 1. Verificar se a tabela existe
print("\n[1] Verificando se a tabela existe...")
try:
    # Verificar tabelas no esquema public
    check_table_sql = """
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema = 'public'
    AND table_name = 'source_codes';
    """

    # Usar POST para SQL
    response = requests.post(
        f"{SUPABASE_URL}/rest/v1/rpc/sql",
        headers=headers,
        json={"query": check_table_sql},
        timeout=10
    )

    if response.status_code == 200:
        data = response.json()
        if data and len(data) > 0:
            print("[+] Tabela 'source_codes' encontrada!")
        else:
            print("[!] Tabela 'source_codes' não encontrada")
            sys.exit(1)
    else:
        print(f"[!] Erro ao verificar tabela: {response.status_code}")
        print(f"Response: {response.text}")

except Exception as e:
    print(f"[!] Erro: {str(e)}")

# 2. Obter estrutura da tabela
print("\n[2] Obtendo estrutura da tabela...")
try:
    columns_sql = """
    SELECT
        column_name,
        data_type,
        is_nullable,
        column_default,
        character_maximum_length
    FROM information_schema.columns
    WHERE table_schema = 'public'
    AND table_name = 'source_codes'
    ORDER BY ordinal_position;
    """

    response = requests.post(
        f"{SUPABASE_URL}/rest/v1/rpc/sql",
        headers=headers,
        json={"query": columns_sql},
        timeout=10
    )

    if response.status_code == 200:
        columns = response.json()
        print("\n[+] Estrutura da tabela source_codes:")
        print("-" * 80)
        print(f"{'Coluna':<25} {'Tipo':<25} {'Nulo':<8} {'Default':<20}")
        print("-" * 80)

        for col in columns:
            col_name = col.get('column_name', 'N/A')
            data_type = col.get('data_type', 'N/A')
            is_nullable = 'YES' if col.get('is_nullable') == 'YES' else 'NO'
            default = str(col.get('column_default', '') or '')[:20]

            print(f"{col_name:<25} {data_type:<25} {is_nullable:<8} {default:<20}")

    else:
        print(f"[!] Erro ao obter colunas: {response.status_code}")

except Exception as e:
    print(f"[!] Erro: {str(e)}")

# 3. Verificar índices
print("\n[3] Verificando índices...")
try:
    indexes_sql = """
    SELECT
        indexname as index_name,
        indexdef as index_definition
    FROM pg_indexes
    WHERE schemaname = 'public'
    AND tablename = 'source_codes';
    """

    response = requests.post(
        f"{SUPABASE_URL}/rest/v1/rpc/sql",
        headers=headers,
        json={"query": indexes_sql},
        timeout=10
    )

    if response.status_code == 200:
        indexes = response.json()
        if indexes:
            print("\n[+] Índices encontrados:")
            for idx in indexes:
                print(f"    - {idx.get('index_name', 'N/A')}")
        else:
            print("[!] Nenhum índice encontrado")

    else:
        print(f"[!] Erro ao verificar índices: {response.status_code}")

except Exception as e:
    print(f"[!] Erro: {str(e)}")

# 4. Verificar RLS
print("\n[4] Verificando Row Level Security...")
try:
    rls_sql = """
    SELECT
        schemaname,
        tablename,
        rowsecurity
    FROM pg_tables
    WHERE schemaname = 'public'
    AND tablename = 'source_codes';
    """

    response = requests.post(
        f"{SUPABASE_URL}/rest/v1/rpc/sql",
        headers=headers,
        json={"query": rls_sql},
        timeout=10
    )

    if response.status_code == 200:
        rls_info = response.json()
        if rls_info:
            rls_enabled = rls_info[0].get('rowsecurity', False)
            status = "Habilitado" if rls_enabled else "Desabilitado"
            print(f"\n[+] Row Level Security: {status}")

    else:
        print(f"[!] Erro ao verificar RLS: {response.status_code}")

except Exception as e:
    print(f"[!] Erro: {str(e)}")

# 5. Verificar políticas RLS
print("\n[5] Verificando políticas RLS...")
try:
    policies_sql = """
    SELECT
        policyname,
        permissive,
        roles,
        cmd,
        qual,
        with_check
    FROM pg_policies
    WHERE tablename = 'source_codes';
    """

    response = requests.post(
        f"{SUPABASE_URL}/rest/v1/rpc/sql",
        headers=headers,
        json={"query": policies_sql},
        timeout=10
    )

    if response.status_code == 200:
        policies = response.json()
        if policies:
            print("\n[+] Políticas RLS encontradas:")
            for policy in policies:
                print(f"    - {policy.get('policyname', 'N/A')}")
                print(f"      Comando: {policy.get('cmd', 'N/A')}")
                print(f"      Papéis: {policy.get('roles', 'N/A')}")
        else:
            print("[!] Nenhuma política RLS encontrada")

    else:
        print(f"[!] Erro ao verificar políticas: {response.status_code}")

except Exception as e:
    print(f"[!] Erro: {str(e)}")

# 6. Verificar triggers
print("\n[6] Verificando triggers...")
try:
    triggers_sql = """
    SELECT
        trigger_name,
        event_manipulation,
        action_timing,
        action_statement
    FROM information_schema.triggers
    WHERE event_object_table = 'source_codes'
    AND trigger_schema = 'public';
    """

    response = requests.post(
        f"{SUPABASE_URL}/rest/v1/rpc/sql",
        headers=headers,
        json={"query": triggers_sql},
        timeout=10
    )

    if response.status_code == 200:
        triggers = response.json()
        if triggers:
            print("\n[+] Triggers encontrados:")
            for trigger in triggers:
                print(f"    - {trigger.get('trigger_name', 'N/A')}")
                print(f"      Evento: {trigger.get('event_manipulation', 'N/A')}")
                print(f"      Timing: {trigger.get('action_timing', 'N/A')}")
        else:
            print("[!] Nenhum trigger encontrado")

    else:
        print(f"[!] Erro ao verificar triggers: {response.status_code}")

except Exception as e:
    print(f"[!] Erro: {str(e)}")

# 7. Testar inserção
print("\n[7] Testando inserção de registro...")
try:
    # Criar um registro de teste
    test_data = {
        "code_id": "test_001",
        "title": "Test Source Code",
        "description": "Test description",
        "content": "console.log('Hello, World!');",
        "file_name": "test.js",
        "file_extension": "js",
        "programming_language": "javascript",
        "line_count": 1,
        "character_count": 26,
        "size_bytes": 26
    }

    response = requests.post(
        f"{SUPABASE_URL}/rest/v1/source_codes",
        headers=headers,
        json=test_data,
        timeout=10
    )

    if response.status_code == 201:
        print("[+] Teste de inserção bem-sucedido!")
        inserted_data = response.json()
        if inserted_data and len(inserted_data) > 0:
            print(f"    ID inserido: {inserted_data[0].get('id')}")
    else:
        print(f"[!] Erro ao inserir teste: {response.status_code}")
        print(f"Response: {response.text}")

except Exception as e:
    print(f"[!] Erro: {str(e)}")

print("\n" + "=" * 60)
print("[+] Verificação concluída!")