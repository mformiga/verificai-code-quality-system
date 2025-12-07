#!/usr/bin/env python3
"""
Update Supabase with exact prompts from PostgreSQL local
"""

import os
import sys
import psycopg2
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv('.env.supabase')

try:
    from supabase import create_client
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

def get_exact_prompts_from_postgres():
    """Get exact prompts from PostgreSQL local"""
    try:
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        cursor = conn.cursor()

        # Buscar os prompts principais do PostgreSQL local
        cursor.execute("""
            SELECT id, name, prompt_type, content, is_active, is_default
            FROM prompt_configurations
            WHERE is_active = true
            ORDER BY
                CASE WHEN id = 7 THEN 1 ELSE 2 END,
                prompt_type, id
        """)

        data = cursor.fetchall()
        conn.close()

        prompts = {}
        for row in data:
            id, name, prompt_type, content, is_active, is_default = row
            # Pegar apenas o melhor prompt de cada tipo
            if prompt_type not in prompts:
                prompts[prompt_type] = {
                    'id': id,
                    'name': name,
                    'content': content,
                    'is_active': is_active,
                    'is_default': is_default
                }

        return prompts

    except Exception as e:
        print(f"Erro ao buscar dados do PostgreSQL: {e}")
        return {}

def update_supabase_prompts():
    """Update Supabase with exact content from PostgreSQL"""
    try:
        supabase = create_supabase_client()
        postgres_prompts = get_exact_prompts_from_postgres()

        if not postgres_prompts:
            print("Nenhum prompt encontrado no PostgreSQL local")
            return

        print("Prompts encontrados no PostgreSQL local:")
        for prompt_type, prompt_data in postgres_prompts.items():
            print(f"  - {prompt_data['name']} ({prompt_type}) - {len(prompt_data['content'])} caracteres")

        # Mapear para nomes de config do Supabase
        config_mapping = {
            'GENERAL': 'general_analysis',
            'ARCHITECTURAL': 'architectural_analysis',
            'BUSINESS': 'business_analysis'
        }

        print("\nAtualizando prompts no Supabase...")

        for prompt_type, prompt_data in postgres_prompts.items():
            config_name = config_mapping.get(prompt_type, f'{prompt_type.lower()}_analysis')

            update_data = {
                'name': prompt_data['name'],
                'content': prompt_data['content'],
                'is_active': prompt_data['is_active'],
                'is_default': prompt_data['is_default']
            }

            try:
                # Atualizar o prompt existente
                result = supabase.table('prompt_configurations').update(update_data).eq('prompt_type', prompt_type).execute()

                if result.data:
                    print(f"[OK] Atualizado: {prompt_data['name']} ({prompt_type})")
                    print(f"     Content length: {len(prompt_data['content'])} caracteres")
                else:
                    print(f"[ERRO] Falha ao atualizar: {prompt_type}")

            except Exception as e:
                print(f"[ERRO] Erro ao atualizar {prompt_type}: {e}")

        # Verificar resultado
        print("\nVerificando prompts atualizados...")
        for prompt_type in postgres_prompts.keys():
            try:
                result = supabase.table('prompt_configurations').select('name, prompt_type, content').eq('prompt_type', prompt_type).execute()
                if result.data:
                    prompt = result.data[0]
                    print(f"  - {prompt['name']} ({prompt['prompt_type']}) - {len(prompt.get('content', ''))} caracteres")
            except Exception as e:
                print(f"Erro ao verificar {prompt_type}: {e}")

    except Exception as e:
        print(f"Erro geral: {e}")

def main():
    """Main function"""
    print("Atualizando Supabase com prompts EXATOS do PostgreSQL local...")
    print("=" * 60)

    update_supabase_prompts()

if __name__ == "__main__":
    main()