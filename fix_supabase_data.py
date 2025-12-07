#!/usr/bin/env python3
"""
Fix and populate Supabase with proper prompt data from PostgreSQL
"""

import os
import sys
import json
import uuid
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

def get_postgres_prompts():
    """Get prompts from PostgreSQL local"""
    try:
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        cursor = conn.cursor()

        # Buscar prompts específicos do ID 7 (Template com Código Fonte) e outros
        cursor.execute("""
            SELECT
                id,
                prompt_type,
                name,
                content,
                is_active,
                is_default,
                created_at,
                updated_at
            FROM prompt_configurations
            WHERE is_active = true
            ORDER BY
                CASE WHEN id = 7 THEN 1 ELSE 2 END,
                LENGTH(content) DESC,
                updated_at DESC
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

def clean_supabase_data(supabase):
    """Clean existing data in Supabase"""
    try:
        # Delete existing prompt configurations
        result = supabase.table('prompt_configurations').delete().neq('id', 0).execute()
        print(f"Dados existentes removidos: {len(result.data) if result.data else 0}")
        return True
    except Exception as e:
        print(f"Erro ao limpar dados do Supabase: {e}")
        return False

def insert_prompts_to_supabase(supabase, prompts):
    """Insert prompts into Supabase with proper UUID handling"""
    try:
        # Generate a default user UUID
        default_user_uuid = "00000000-0000-0000-0000-000000000001"

        success_count = 0
        error_count = 0

        for prompt in prompts:
            try:
                # Prepare data for Supabase
                supabase_data = {
                    'id': str(uuid.uuid4()),  # Generate new UUID for each prompt
                    'user_id': default_user_uuid,
                    'prompt_type': prompt['prompt_type'],
                    'name': prompt['name'],
                    'description': f"Prompt migrated from PostgreSQL - ID: {prompt['id']}",
                    'content': prompt['content'],
                    'is_active': prompt['is_active'],
                    'is_default': prompt['is_default'],
                    'created_at': prompt.get('created_at', datetime.now().isoformat()),
                    'updated_at': prompt.get('updated_at', datetime.now().isoformat()),
                    'created_by': default_user_uuid,
                    'updated_by': default_user_uuid
                }

                # Insert into Supabase
                result = supabase.table('prompt_configurations').insert(supabase_data).execute()

                if result.data:
                    success_count += 1
                    print(f"[OK] Inserido: {prompt['name']} ({prompt['prompt_type']}) - Novo ID: {result.data[0]['id']}")
                else:
                    error_count += 1
                    print(f"[ERRO] Erro ao inserir: {prompt['name']}")

            except Exception as e:
                error_count += 1
                print(f"[ERRO] Erro ao inserir {prompt.get('name', 'desconhecido')}: {e}")

        print(f"\nResumo da insercao:")
        print(f"   Sucesso: {success_count}")
        print(f"   Erros: {error_count}")
        print(f"   Total: {len(prompts)}")

        return success_count > 0

    except Exception as e:
        print(f"Erro geral na inserção: {e}")
        return False

def verify_supabase_data(supabase):
    """Verify data in Supabase"""
    try:
        print("\nVerificando dados no Supabase...")
        result = supabase.table('prompt_configurations').select('*').execute()

        if result.data:
            print(f"Encontrados {len(result.data)} prompts no Supabase:")
            for prompt in result.data:
                content_preview = prompt.get('content', '')[:100] + "..." if len(prompt.get('content', '')) > 100 else prompt.get('content', '')
                print(f"   - {prompt.get('name', 'Sem nome')} ({prompt.get('prompt_type', 'Sem tipo')})")
                print(f"     ID: {prompt.get('id')}")
                print(f"     Content: {content_preview}")
                print()
            return True
        else:
            print("Nenhum prompt encontrado no Supabase")
            return False

    except Exception as e:
        print(f"Erro ao verificar dados: {e}")
        return False

def main():
    """Main function"""
    print("Atualizando Supabase com dados do PostgreSQL local...")
    print("=" * 60)

    try:
        # Criar cliente Supabase
        supabase = create_supabase_client()
        print("Cliente Supabase criado com sucesso")

        # Buscar dados do PostgreSQL local
        print("\nBuscando dados do PostgreSQL local...")
        prompts = get_postgres_prompts()

        if not prompts:
            print("Nenhum prompt encontrado no PostgreSQL local")
            return

        print(f"Encontrados {len(prompts)} prompts no PostgreSQL local")

        # Mostrar os prompts que serão migrados
        print("\nPrompts a serem migrados:")
        for i, prompt in enumerate(prompts, 1):
            print(f"   {i}. {prompt['name']} ({prompt['prompt_type']}) - ID: {prompt['id']}")
            content_preview = prompt['content'][:100] + "..." if len(prompt['content']) > 100 else prompt['content']
            print(f"      Conteudo: {content_preview}")

        # Limpar dados existentes no Supabase
        print(f"\nLimpando dados existentes no Supabase...")
        if clean_supabase_data(supabase):
            print("Dados existentes removidos")
        else:
            print("Nao foi possivel remover dados existentes, continuando...")

        # Inserir novos dados
        print(f"\nInserindo dados no Supabase...")
        if insert_prompts_to_supabase(supabase, prompts):
            print("Insercao concluida com sucesso!")
        else:
            print("Erros durante a insercao")

        # Verificar resultado
        verify_supabase_data(supabase)

    except Exception as e:
        print(f"Erro geral: {e}")

if __name__ == "__main__":
    main()