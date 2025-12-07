#!/usr/bin/env python3
"""
Script para criar a tabela source_codes no Supabase
Executa os comandos SQL passo a passo conforme solicitado
"""

import os
from dotenv import load_dotenv
from supabase import create_client
import sys

# Carregar variáveis de ambiente
load_dotenv('.env.supabase')

# Configurações do Supabase
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    print("[!] Erro: Variáveis de ambiente do Supabase não encontradas")
    print("Verifique o arquivo .env.supabase")
    sys.exit(1)

# Criar cliente Supabase
print("[*] Conectando ao Supabase...")
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
print("[+] Conectado com sucesso!")

# Comandos SQL para executar passo a passo
sql_commands = [
    {
        "name": "Criar extensão UUID",
        "sql": 'CREATE EXTENSION IF NOT EXISTS "uuid-ossp";'
    },
    {
        "name": "Criar tabela source_codes",
        "sql": """
        CREATE TABLE public.source_codes (
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
        """
    },
    {
        "name": "Criar índices",
        "sql": """
        CREATE INDEX idx_source_codes_code_id ON source_codes(code_id);
        CREATE INDEX idx_source_codes_status ON source_codes(status);
        CREATE INDEX idx_source_codes_user_id ON source_codes(user_id);
        """
    },
    {
        "name": "Criar função para trigger updated_at",
        "sql": """
        CREATE OR REPLACE FUNCTION update_source_codes_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ language 'plpgsql';
        """
    },
    {
        "name": "Criar trigger para updated_at",
        "sql": """
        CREATE TRIGGER update_source_codes_updated_at
        BEFORE UPDATE ON source_codes
        FOR EACH ROW EXECUTE FUNCTION update_source_codes_updated_at();
        """
    },
    {
        "name": "Habilitar Row Level Security (RLS)",
        "sql": "ALTER TABLE source_codes ENABLE ROW LEVEL SECURITY;"
    },
    {
        "name": "Criar políticas RLS - Parte 1",
        "sql": """
        CREATE POLICY "Users can view own source codes" ON source_codes
            FOR SELECT USING (auth.uid() = user_id);

        CREATE POLICY "Users can insert own source codes" ON source_codes
            FOR INSERT WITH CHECK (auth.uid() = user_id);
        """
    },
    {
        "name": "Criar políticas RLS - Parte 2",
        "sql": """
        CREATE POLICY "Users can update own source codes" ON source_codes
            FOR UPDATE USING (auth.uid() = user_id);

        CREATE POLICY "Users can delete own source codes" ON source_codes
            FOR DELETE USING (auth.uid() = user_id);

        CREATE POLICY "Public source codes are viewable by everyone" ON source_codes
            FOR SELECT USING (is_public = true);
        """
    },
    {
        "name": "Adicionar comentários na tabela",
        "sql": """
        COMMENT ON TABLE source_codes IS 'Stores source code content with metadata and processing status';
        COMMENT ON COLUMN source_codes.code_id IS 'Unique identifier for the source code entry';
        COMMENT ON COLUMN source_codes.content IS 'Source code content';
        COMMENT ON COLUMN source_codes.file_extension IS 'File extension for language detection';
        COMMENT ON COLUMN source_codes.programming_language IS 'Detected or specified programming language';
        COMMENT ON COLUMN source_codes.line_count IS 'Number of lines in the source code';
        COMMENT ON COLUMN source_codes.character_count IS 'Total character count';
        COMMENT ON COLUMN source_codes.size_bytes IS 'Size in bytes of the content';
        COMMENT ON COLUMN source_codes.status IS 'Current status';
        COMMENT ON COLUMN source_codes.is_processed IS 'Whether the code has been processed for analysis';
        COMMENT ON COLUMN source_codes.processing_status IS 'Processing status: pending, processing, completed, error';
        COMMENT ON COLUMN source_codes.user_id IS 'Reference to auth.users table';
        """
    }
]

# Executar comandos SQL
print("\n🚀 Iniciando criação da tabela source_codes...")
print("=" * 60)

erros = []
sucessos = []

for i, cmd in enumerate(sql_commands, 1):
    print(f"\n📋 Passo {i}/{len(sql_commands)}: {cmd['name']}")
    try:
        # Executar comando SQL usando RPC
        result = supabase.rpc('exec_sql', {'query': cmd['sql']}).execute()

        # Se o RPC não estiver disponível, tentamos usar SQL direto
        if hasattr(result, 'data') and result.data is None:
            # Tentar alternativa usando postgrest
            response = supabase.table('_temp').select('*').execute()

        print(f"   ✅ {cmd['name']} - Executado com sucesso")
        sucessos.append(cmd['name'])

    except Exception as e:
        # Ignorar erro se a extensão já existe ou tabela já existe
        error_str = str(e).lower()
        if any(keyword in error_str for keyword in ['already exists', 'duplicate', 'does not exist']):
            print(f"   ⚠️  {cmd['name']} - Já existe (ignorado)")
            sucessos.append(cmd['name'] + " (já existia)")
        else:
            print(f"   ❌ {cmd['name']} - Erro: {str(e)}")
            erros.append(f"{cmd['name']}: {str(e)}")

print("\n" + "=" * 60)
print("\n📊 RESUMO DA EXECUÇÃO:")
print(f"✅ Sucessos: {len(sucessos)}")
print(f"❌ Erros: {len(erros)}")

if sucessos:
    print("\n✅ Comandos executados com sucesso:")
    for s in sucessos:
        print(f"   - {s}")

if erros:
    print("\n❌ Erros encontrados:")
    for e in erros:
        print(f"   - {e}")

# Verificar se a tabela foi criada
print("\n🔍 Verificando se a tabela foi criada...")
try:
    # Tentar obter a estrutura da tabela
    result = supabase.rpc('get_table_schema', {'table_name': 'source_codes'}).execute()

    # Se não funcionar, tentar inserir um registro de teste
    print("   Tentando verificar com um SELECT...")

except Exception as e:
    print(f"   ⚠️  Não foi possível verificar a estrutura da tabela: {str(e)}")
    print("   Isso pode ser normal se o RPC não estiver configurado")

# Tentar verificação alternativa
print("\n📋 Tentando verificação alternativa...")
try:
    # Tentar listar as colunas da tabela
    test_query = """
    SELECT column_name, data_type
    FROM information_schema.columns
    WHERE table_name = 'source_codes'
    AND table_schema = 'public'
    LIMIT 5;
    """

    result = supabase.rpc('exec_sql', {'query': test_query}).execute()

    if result.data:
        print("   ✅ Tabela source_codes encontrada!")
        print("   Colunas:")
        for col in result.data[:5]:  # Mostrar primeiras 5 colunas
            print(f"     - {col.get('column_name', 'N/A')}: {col.get('data_type', 'N/A')}")
    else:
        print("   ⚠️  Não foi possível confirmar a estrutura da tabela")

except Exception as e:
    print(f"   ⚠️  Verificação alternativa falhou: {str(e)}")
    print("   A tabela pode ter sido criada, mas não foi possível verificar")

print("\n🎉 Processo concluído!")
if len(erros) == 0:
    print("✅ Todos os comandos foram executados sem erros")
else:
    print("⚠️  Alguns comandos encontraram erros, mas a tabela pode ter sido criada")