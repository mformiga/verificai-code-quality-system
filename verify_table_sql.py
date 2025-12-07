#!/usr/bin/env python3
"""
Script para verificar a tabela source_codes no Supabase usando SQL direto
"""

import os
import json
from dotenv import load_dotenv
import requests
import sys
import psycopg2
from psycopg2.extras import RealDictCursor

# Carregar variáveis de ambiente
load_dotenv('.env.supabase')

# Configurações do Supabase para conexão PostgreSQL
# Extrair do URL: https://jjxmfidggofuaxcdtkrd.supabase.co
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

# Construir string de conexão PostgreSQL
# Formato: postgresql://postgres:[PASSWORD]@db.[PROJECT_REF].supabase.co:5432/postgres
project_ref = SUPABASE_URL.split('//')[1].split('.')[0] if SUPABASE_URL else None

if project_ref:
    # Tentar obter senha do service role key (não é a senha correta, mas vamos tentar)
    # Na verdade, precisamos da senha real do banco
    print("[!] Informação: Para conectar diretamente ao PostgreSQL,")
    print("    você precisa da senha do banco de dados do Supabase.")
    print("    Vá em Project Settings > Database no painel do Supabase.")

# Tentar outra abordagem usando a API REST para verificar
print("\n[*] Tentando verificação via API REST...")

# Headers para autenticação
headers = {
    'apikey': SUPABASE_SERVICE_ROLE_KEY,
    'Authorization': f'Bearer {SUPABASE_SERVICE_ROLE_KEY}',
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

# Tentar acessar a tabela diretamente
try:
    print("\n[*] Tentando acessar tabela source_codes...")
    url = f"{SUPABASE_URL}/rest/v1/source_codes?select=count&limit=0"
    response = requests.get(url, headers=headers, timeout=10)

    if response.status_code == 200:
        print("[+] Tabela source_codes existe e está acessível!")
        print(f"    Response headers: {dict(response.headers)}")
    else:
        print(f"[!] Status: {response.status_code}")
        print(f"    Response: {response.text[:200]}")

except Exception as e:
    print(f"[!] Erro: {str(e)}")

# Tentar listar tabelas disponíveis
print("\n[*] Tentando listar tabelas disponíveis...")
try:
    # Usar o endpoint tables (se disponível)
    url = f"{SUPABASE_URL}/rest/v1/"
    response = requests.options(url, headers=headers, timeout=10)

    if response.status_code == 200:
        print("[+] Endpoint OPTIONS disponível")
        print(f"    Headers: {dict(response.headers)}")

        # Verificar Allow header
        allow = response.headers.get('Allow', '')
        if 'source_codes' in allow:
            print("[+] Tabela source_codes parece estar disponível")

except Exception as e:
    print(f"[!] Erro ao verificar OPTIONS: {str(e)}")

# Tentar usar o endpoint rpc com SQL (algumas instâncias do Supabase suportam)
print("\n[*] Tentando executar SQL via RPC...")
try:
    # Função SQL padrão em muitos projetos Supabase
    sql_query = {
        "query": """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_name = 'source_codes';
        """
    }

    # Tentar diferentes endpoints
    endpoints = [
        f"{SUPABASE_URL}/rest/v1/rpc/sql",
        f"{SUPABASE_URL}/rest/v1/rpc/exec",
        f"{SUPABASE_URL}/rest/v1/rpc/query",
        f"{SUPABASE_URL}/rest/v1/rpc/exec_sql"
    ]

    for endpoint in endpoints:
        try:
            print(f"\n    Tentando endpoint: {endpoint}")
            response = requests.post(
                endpoint,
                headers=headers,
                json=sql_query,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                if data:
                    print(f"[+] Sucesso no endpoint {endpoint}!")
                    print(f"    Dados: {data}")
                    break
                else:
                    print(f"[!] Sem dados no endpoint {endpoint}")
            else:
                print(f"[!] Status {response.status_code} no endpoint {endpoint}")

        except Exception as e:
            print(f"[!] Erro no endpoint {endpoint}: {str(e)}")

except Exception as e:
    print(f"[!] Erro geral: {str(e)}")

# Mostrar instruções para verificação manual
print("\n" + "=" * 60)
print("[!] INSTRUÇÕES PARA VERIFICAÇÃO MANUAL:")
print("=" * 60)
print("\n1. No painel do Supabase (https://app.supabase.com):")
print(f"   - Vá para o projeto: {project_ref}")
print("   - Clique em 'Table Editor' no menu lateral")
print("   - Procure pela tabela 'source_codes'")
print("\n2. Para ver a estrutura da tabela:")
print("   - Clique na tabela 'source_codes'")
print("   - Visualize as colunas e seus tipos")
print("\n3. Para testar inserção:")
print("   - Clique em 'Insert row'")
print("   - Preencha os dados e teste")

# Exibir a estrutura esperada da tabela
print("\n4. Estrutura esperada da tabela source_codes:")
print("-" * 60)
print("""
Colunas esperadas:
- id: UUID (Primary Key, Default: gen_random_uuid())
- code_id: VARCHAR(255) UNIQUE NOT NULL
- title: VARCHAR(255) NOT NULL
- description: TEXT
- content: TEXT NOT NULL
- file_name: VARCHAR(255) NOT NULL
- file_extension: VARCHAR(50) NOT NULL
- programming_language: VARCHAR(100)
- line_count: INTEGER
- character_count: INTEGER
- size_bytes: BIGINT
- status: VARCHAR(50) DEFAULT 'active'
- is_public: BOOLEAN DEFAULT false
- is_processed: BOOLEAN DEFAULT false
- processing_status: VARCHAR(50) DEFAULT 'pending'
- user_id: UUID (Foreign Key para auth.users)
- created_at: TIMESTAMP WITH TIME ZONE DEFAULT NOW()
- updated_at: TIMESTAMP WITH TIME ZONE DEFAULT NOW()

Índices:
- idx_source_codes_code_id (em code_id)
- idx_source_codes_status (em status)
- idx_source_codes_user_id (em user_id)

Triggers:
- update_source_codes_updated_at (BEFORE UPDATE)

RLS (Row Level Security): Habilitado
Políticas:
- "Users can view own source codes"
- "Users can insert own source codes"
- "Users can update own source codes"
- "Users can delete own source codes"
- "Public source codes are viewable by everyone"
""")

# Criar um script SQL alternativo
print("\n5. Script SQL para verificação direta no painel:")
print("-" * 60)
print("""
-- Verificar se a tabela existe
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name = 'source_codes';

-- Verificar estrutura das colunas
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_schema = 'public'
AND table_name = 'source_codes'
ORDER BY ordinal_position;

-- Verificar índices
SELECT indexname, indexdef
FROM pg_indexes
WHERE schemaname = 'public'
AND tablename = 'source_codes';

-- Verificar RLS
SELECT rowsecurity
FROM pg_tables
WHERE schemaname = 'public'
AND tablename = 'source_codes';

-- Verificar políticas
SELECT policyname, cmd, roles
FROM pg_policies
WHERE tablename = 'source_codes';
""")

print("\n" + "=" * 60)
print("[+] Fim da verificação")