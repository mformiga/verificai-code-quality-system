#!/usr/bin/env python3
"""
Migrate prompt_configurations data from PostgreSQL to Supabase (without settings column)
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
    print(f"Erro de importacao: {e}")
    print("Instale as dependencias com: pip install supabase psycopg2-binary python-dotenv")
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
        raise ValueError("Variaveis de ambiente SUPABASE_URL e SUPABASE_SERVICE_ROLE_KEY sao obrigatorias")

    return create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

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
                # Remover coluna settings se existir
                prompt_data_for_insert = {k: v for k, v in prompt_data.items() if k != 'settings'}

                # Inserir no Supabase
                result = supabase.table('prompt_configurations').insert(prompt_data_for_insert).execute()

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

def main():
    """Main function"""
    print("Migrando prompt_configurations do PostgreSQL para Supabase...")

    try:
        # Criar cliente Supabase
        supabase = create_supabase_client()
        print("Cliente Supabase criado com sucesso")

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