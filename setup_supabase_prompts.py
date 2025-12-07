#!/usr/bin/env python3
"""
Setup prompt_configurations table in Supabase and migrate data from PostgreSQL
"""

import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv('.env.supabase')

try:
    from supabase import create_client
    import psycopg2
except ImportError as e:
    print(f"Erro de importação: {e}")
    print("Instale as dependências com: pip install supabase psycopg2-binary python-dotenv")
    sys.exit(1)

# Configurações Supabase
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

# Configurações PostgreSQL Local
POSTGRES_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': os.getenv('POSTGRES_PORT', '5432'),
    'database': os.getenv('POSTGRES_DB', 'verificai'),
    'user': os.getenv('POSTGRES_USER', 'verificai'),
    'password': os.getenv('POSTGRES_PASSWORD', 'verificai123')
}

def create_supabase_client():
    """Create Supabase client"""
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        raise ValueError("Variáveis de ambiente SUPABASE_URL e SUPABASE_SERVICE_ROLE_KEY são obrigatórias")

    return create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

def create_prompt_configurations_table(supabase):
    """Create prompt_configurations table in Supabase"""

    # SQL para criar a tabela
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS prompt_configurations (
        id BIGSERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
        prompt_type TEXT NOT NULL CHECK (prompt_type IN ('GENERAL', 'ARCHITECTURAL', 'BUSINESS')),
        name VARCHAR(255) NOT NULL,
        description TEXT,
        content TEXT NOT NULL,
        is_active BOOLEAN NOT NULL DEFAULT true,
        is_default BOOLEAN NOT NULL DEFAULT false,
        settings JSONB,
        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
        created_by INTEGER REFERENCES profiles(id) ON DELETE SET NULL,
        updated_by INTEGER REFERENCES profiles(id) ON DELETE SET NULL,

        -- Unique constraints
        UNIQUE(user_id, name),
        UNIQUE(user_id, prompt_type)
    );

    -- Create indexes
    CREATE INDEX IF NOT EXISTS idx_prompt_configurations_user_id ON prompt_configurations(user_id);
    CREATE INDEX IF NOT EXISTS idx_prompt_configurations_type ON prompt_configurations(prompt_type);
    CREATE INDEX IF NOT EXISTS idx_prompt_configurations_active ON prompt_configurations(is_active);

    -- Create trigger for updated_at
    CREATE OR REPLACE FUNCTION update_updated_at_column()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.updated_at = NOW();
        RETURN NEW;
    END;
    $$ language 'plpgsql';

    DROP TRIGGER IF EXISTS update_prompt_configurations_updated_at ON prompt_configurations;
    CREATE TRIGGER update_prompt_configurations_updated_at
        BEFORE UPDATE ON prompt_configurations
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();
    """

    try:
        # Executar SQL via Supabase RPC (não é possível criar tabelas diretamente via client)
        # Vamos usar a REST API do Supabase para executar SQL
        print("⚠️  Nota: A criação de tabelas via client Python tem limitações.")
        print("   É recomendado criar a tabela manualmente no painel do Supabase ou via SQL Editor.")
        print("\nSQL para criar a tabela (copie e cole no SQL Editor do Supabase):")
        print("=" * 80)
        print(create_table_sql)
        print("=" * 80)

        return True
    except Exception as e:
        print(f"Erro ao criar tabela: {e}")
        return False

def get_postgres_data():
    """Get data from PostgreSQL local"""
    try:
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        cursor = conn.cursor()

        # Buscar todos os prompts ativos
        cursor.execute("""
            SELECT
                user_id,
                prompt_type,
                name,
                description,
                content,
                is_active,
                is_default,
                settings,
                created_at,
                updated_at,
                created_by,
                updated_by
            FROM prompt_configurations
            WHERE is_active = true
            ORDER BY id
        """)

        data = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]

        conn.close()

        # Converter para lista de dicionários
        result = []
        for row in data:
            row_dict = dict(zip(columns, row))
            # Converter datetime para string
            if row_dict['created_at']:
                row_dict['created_at'] = row_dict['created_at'].isoformat()
            if row_dict['updated_at']:
                row_dict['updated_at'] = row_dict['updated_at'].isoformat()
            # Converter JSON settings para string se necessário
            if row_dict['settings']:
                row_dict['settings'] = json.dumps(row_dict['settings']) if isinstance(row_dict['settings'], dict) else row_dict['settings']
            result.append(row_dict)

        return result

    except Exception as e:
        print(f"Erro ao buscar dados do PostgreSQL: {e}")
        return []

def migrate_to_supabase(supabase, data):
    """Migrate data to Supabase"""
    try:
        success_count = 0
        error_count = 0

        for prompt_data in data:
            try:
                # Inserir no Supabase
                result = supabase.table('prompt_configurations').insert(prompt_data).execute()

                if result.data:
                    success_count += 1
                    print(f"[OK] Migrado: {prompt_data['name']} ({prompt_data['prompt_type']})")
                else:
                    error_count += 1
                    print(f"[ERRO] Erro ao migrar: {prompt_data['name']}")

            except Exception as e:
                error_count += 1
                print(f"[ERRO] Erro ao migrar {prompt_data.get('name', 'desconhecido')}: {e}")

        print(f"\nResumo da migracao:")
        print(f"   Sucesso: {success_count}")
        print(f"   Erros: {error_count}")
        print(f"   Total: {len(data)}")

        return success_count > 0

    except Exception as e:
        print(f"Erro geral na migracao: {e}")
        return False

def check_supabase_table(supabase):
    """Check if table exists in Supabase"""
    try:
        # Tentar buscar dados da tabela
        result = supabase.table('prompt_configurations').select('count').execute()
        return True
    except Exception as e:
        print(f"Erro ao verificar tabela no Supabase: {e}")
        return False

def main():
    """Main function"""
    print("Configurando prompt_configurations no Supabase...\n")

    try:
        # Criar cliente Supabase
        supabase = create_supabase_client()
        print("Cliente Supabase criado com sucesso")

        # Verificar se tabela existe
        print("\nVerificando se tabela prompt_configurations existe...")
        if check_supabase_table(supabase):
            print("Tabela prompt_configurations ja existe no Supabase")
        else:
            print("ATENCAO: Tabela prompt_configurations nao encontrada no Supabase")
            print("E necessario cria-la manualmente via SQL Editor do Supabase")
            print("Use o SQL fornecido acima na funcao create_prompt_configurations_table")
            return

        # Buscar dados do PostgreSQL local
        print("\nBuscando dados do PostgreSQL local...")
        data = get_postgres_data()

        if not data:
            print("Nenhum dado encontrado no PostgreSQL local")
            return

        print(f"Encontrados {len(data)} prompts no PostgreSQL local")

        # Migrar para Supabase
        print("\nMigrando dados para Supabase...")
        if migrate_to_supabase(supabase, data):
            print("Migracao concluida com sucesso!")
        else:
            print("Erros durante a migracao")

        # Verificar resultado
        print("\nVerificando dados no Supabase...")
        try:
            result = supabase.table('prompt_configurations').select('id, name, prompt_type').execute()
            if result.data:
                print(f"{len(result.data)} prompts encontrados no Supabase:")
                for prompt in result.data:
                    print(f"   - {prompt['name']} ({prompt['prompt_type']})")
            else:
                print("Nenhum prompt encontrado no Supabase apos migracao")
        except Exception as e:
            print(f"Erro ao verificar dados no Supabase: {e}")

    except Exception as e:
        print(f"Erro geral: {e}")

if __name__ == "__main__":
    main()