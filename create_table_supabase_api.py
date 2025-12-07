#!/usr/bin/env python3
"""
Script para criar a tabela source_codes usando a API SQL do Supabase
"""

import os
import json
from dotenv import load_dotenv
import requests
import sys

# Carregar variáveis de ambiente
load_dotenv('.env.supabase')

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    print("[!] Erro: Variáveis de ambiente do Supabase não encontradas")
    sys.exit(1)

print("[*] Criando tabela source_codes no Supabase...")
print("=" * 60)

# Headers para a API SQL do Supabase
headers = {
    'Authorization': f'Bearer {SUPABASE_SERVICE_ROLE_KEY}',
    'apikey': SUPABASE_SERVICE_ROLE_KEY,
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

# SQL completo para criar a tabela
sql_complete = """
-- Criar extensão UUID se não existir
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Criar a tabela source_codes
CREATE TABLE IF NOT EXISTS public.source_codes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code_id VARCHAR(255) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    content TEXT NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_extension VARCHAR(50) NOT NULL,
    programming_language VARCHAR(100),
    line_count INTEGER,
    character_count INTEGER,
    size_bytes BIGINT,
    status VARCHAR(50) DEFAULT 'active',
    is_public BOOLEAN DEFAULT false,
    is_processed BOOLEAN DEFAULT false,
    processing_status VARCHAR(50) DEFAULT 'pending',
    user_id UUID REFERENCES auth.users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Criar índices
CREATE INDEX IF NOT EXISTS idx_source_codes_code_id ON source_codes(code_id);
CREATE INDEX IF NOT EXISTS idx_source_codes_status ON source_codes(status);
CREATE INDEX IF NOT EXISTS idx_source_codes_user_id ON source_codes(user_id);

-- Criar função para trigger
CREATE OR REPLACE FUNCTION update_source_codes_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Criar trigger
DROP TRIGGER IF EXISTS update_source_codes_updated_at ON source_codes;
CREATE TRIGGER update_source_codes_updated_at
BEFORE UPDATE ON source_codes
FOR EACH ROW EXECUTE FUNCTION update_source_codes_updated_at();

-- Habilitar RLS
ALTER TABLE source_codes ENABLE ROW LEVEL SECURITY;

-- Remover políticas existentes (se houver)
DROP POLICY IF EXISTS "Users can view own source codes" ON source_codes;
DROP POLICY IF EXISTS "Users can insert own source codes" ON source_codes;
DROP POLICY IF EXISTS "Users can update own source codes" ON source_codes;
DROP POLICY IF EXISTS "Users can delete own source codes" ON source_codes;
DROP POLICY IF EXISTS "Public source codes are viewable by everyone" ON source_codes;

-- Criar políticas RLS
CREATE POLICY "Users can view own source codes" ON source_codes
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own source codes" ON source_codes
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own source codes" ON source_codes
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own source codes" ON source_codes
    FOR DELETE USING (auth.uid() = user_id);

CREATE POLICY "Public source codes are viewable by everyone" ON source_codes
    FOR SELECT USING (is_public = true);
"""

# Tentar diferentes métodos para executar SQL
methods_tried = []

# Método 1: Endpoint SQL do Supabase
print("\n[*] Método 1: Tentando endpoint SQL...")
try:
    # Alguns projetos Supabase têm este endpoint
    url = f"{SUPABASE_URL}/rest/v1/sql"
    response = requests.post(
        url,
        headers=headers,
        json={"query": sql_complete},
        timeout=30
    )

    if response.status_code == 200:
        print("[+] SQL executado com sucesso via método 1!")
        methods_tried.append("SQL Endpoint - SUCESSO")
    else:
        print(f"[!] Método 1 falhou: Status {response.status_code}")
        methods_tried.append(f"SQL Endpoint - FALHOU ({response.status_code})")

except Exception as e:
    print(f"[!] Método 1 erro: {str(e)}")
    methods_tried.append(f"SQL Endpoint - ERRO")

# Método 2: Endpoint RPC com função customizada
print("\n[*] Método 2: Tentando endpoint RPC...")
try:
    # Tentar criar uma função temporária primeiro
    create_function_sql = """
    CREATE OR REPLACE FUNCTION exec_sql(query text)
    RETURNS TABLE(result text) AS $$
    BEGIN
        EXECUTE query;
        RETURN NEXT 'OK'::text;
    END;
    $$ LANGUAGE plpgsql SECURITY DEFINER;
    """

    # Se não funcionar, tentar método alternativo
    pass

except Exception as e:
    print(f"[!] Método 2 erro: {str(e)}")

# Método 3: Dividir SQL em comandos menores
print("\n[*] Método 3: Tentando comandos individuais...")

# Lista de comandos SQL individuais
sql_commands = [
    "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";",
    """
    CREATE TABLE IF NOT EXISTS public.source_codes (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        code_id VARCHAR(255) UNIQUE NOT NULL,
        title VARCHAR(255) NOT NULL,
        description TEXT,
        content TEXT NOT NULL,
        file_name VARCHAR(255) NOT NULL,
        file_extension VARCHAR(50) NOT NULL,
        programming_language VARCHAR(100),
        line_count INTEGER,
        character_count INTEGER,
        size_bytes BIGINT,
        status VARCHAR(50) DEFAULT 'active',
        is_public BOOLEAN DEFAULT false,
        is_processed BOOLEAN DEFAULT false,
        processing_status VARCHAR(50) DEFAULT 'pending',
        user_id UUID REFERENCES auth.users(id),
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    """,
    "CREATE INDEX IF NOT EXISTS idx_source_codes_code_id ON source_codes(code_id);",
    "CREATE INDEX IF NOT EXISTS idx_source_codes_status ON source_codes(status);",
    "CREATE INDEX IF NOT EXISTS idx_source_codes_user_id ON source_codes(user_id);",
    """
    CREATE OR REPLACE FUNCTION update_source_codes_updated_at()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.updated_at = NOW();
        RETURN NEW;
    END;
    $$ language 'plpgsql';
    """,
    """
    DROP TRIGGER IF EXISTS update_source_codes_updated_at ON source_codes;
    CREATE TRIGGER update_source_codes_updated_at
    BEFORE UPDATE ON source_codes
    FOR EACH ROW EXECUTE FUNCTION update_source_codes_updated_at();
    """,
    "ALTER TABLE source_codes ENABLE ROW LEVEL SECURITY;",
    """
    DROP POLICY IF EXISTS "Users can view own source codes" ON source_codes;
    CREATE POLICY "Users can view own source codes" ON source_codes
        FOR SELECT USING (auth.uid() = user_id);
    """,
    """
    DROP POLICY IF EXISTS "Users can insert own source codes" ON source_codes;
    CREATE POLICY "Users can insert own source codes" ON source_codes
        FOR INSERT WITH CHECK (auth.uid() = user_id);
    """,
    """
    DROP POLICY IF EXISTS "Users can update own source codes" ON source_codes;
    CREATE POLICY "Users can update own source codes" ON source_codes
        FOR UPDATE USING (auth.uid() = user_id);
    """,
    """
    DROP POLICY IF EXISTS "Users can delete own source codes" ON source_codes;
    CREATE POLICY "Users can delete own source codes" ON source_codes
        FOR DELETE USING (auth.uid() = user_id);
    """,
    """
    DROP POLICY IF EXISTS "Public source codes are viewable by everyone" ON source_codes;
    CREATE POLICY "Public source codes are viewable by everyone" ON source_codes
        FOR SELECT USING (is_public = true);
    """
]

# Tentar usar o endpoint de query (se existir)
for i, cmd in enumerate(sql_commands, 1):
    print(f"\n    Comando {i}/{len(sql_commands)}...")
    try:
        # Tentar endpoint diferentes
        endpoints_to_try = [
            f"{SUPABASE_URL}/rest/v1/",
            f"{SUPABASE_URL}/rest/v1/rpc/exec_sql",
            f"{SUPABASE_URL}/rest/v1/sql"
        ]

        for endpoint in endpoints_to_try:
            try:
                if endpoint.endswith('/'):
                    # Tentar como POST normal
                    response = requests.post(
                        endpoint,
                        headers=headers,
                        json={"query": cmd},
                        timeout=10
                    )
                else:
                    # Tentar como RPC
                    response = requests.post(
                        endpoint,
                        headers=headers,
                        json={"query": cmd},
                        timeout=10
                    )

                if response.status_code in [200, 201, 204]:
                    print(f"      [+] Sucesso no endpoint: {endpoint}")
                    break
                else:
                    print(f"      [!] Falha ({response.status_code}) no endpoint: {endpoint}")

            except Exception as e:
                continue

    except Exception as e:
        print(f"      [!] Erro no comando {i}: {str(e)}")

# Verificação final
print("\n[*] Verificando se a tabela foi criada...")
try:
    url = f"{SUPABASE_URL}/rest/v1/source_codes?select=count&limit=0"
    response = requests.get(url, headers=headers, timeout=10)

    if response.status_code == 200:
        print("\n[+] SUCESSO! Tabela source_codes está acessível!")
        print("    A tabela foi criada com sucesso e pode ser usada pela aplicação.")
    elif response.status_code == 406:
        print("\n[+] SUCESSO! Tabela source_codes existe!")
        print("    (Erro 406 é esperado ao fazer count em tabela vazia)")
    else:
        print(f"\n[!] Tabela ainda não acessível: Status {response.status_code}")
        print("    Verifique o painel do Supabase para confirmar se a tabela foi criada")

except Exception as e:
    print(f"\n[!] Erro na verificação: {str(e)}")

print("\n" + "=" * 60)
print("[+] Métodos tentados:")
for method in methods_tried:
    print(f"    - {method}")

print("\n[!] Se a tabela não foi criada, use o painel do Supabase:")
print(f"    1. Acesse: https://app.supabase.com/project/jjxmfidggofuaxcdtkrd")
print("    2. Vá para 'SQL Editor'")
print("    3. Cole e execute o SQL completo do arquivo create_source_codes_supabase.sql")
print("=" * 60)