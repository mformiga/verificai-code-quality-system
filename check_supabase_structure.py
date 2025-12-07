#!/usr/bin/env python3
"""
Check Supabase database structure and create default user
"""

import os
import uuid
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv('.env.supabase')

try:
    from supabase import create_client
except ImportError as e:
    print(f"Erro de importacao: {e}")
    print("Instale as dependencias com: pip install supabase python-dotenv")
    exit(1)

# Configurações Supabase
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

def create_supabase_client():
    """Create Supabase client"""
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        raise ValueError("Variaveis de ambiente SUPABASE_URL e SUPABASE_SERVICE_ROLE_KEY sao obrigatorias")

    return create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

def check_tables(supabase):
    """Check available tables in Supabase"""
    try:
        # Try to query information schema
        # Note: This might not work depending on Supabase permissions
        print("Tentando verificar tabelas disponiveis...")

        # Check if profiles table exists by trying to query it
        try:
            result = supabase.table('profiles').select('count').execute()
            print("Tabela 'profiles' existe")
            if result.data:
                print(f"Registros em profiles: {len(result.data)}")
            return True
        except Exception as e:
            print(f"Tabela 'profiles' nao encontrada ou sem acesso: {e}")

            # Try to create a default profile
            print("\nTentando criar profile padrao...")
            default_profile = {
                'id': str(uuid.uuid4()),
                'email': 'admin@verificai.local',
                'name': 'Administrador VerificAI',
                'role': 'admin'
            }

            try:
                result = supabase.table('profiles').insert(default_profile).execute()
                if result.data:
                    print(f"Profile padrao criado com ID: {default_profile['id']}")
                    return default_profile['id']
            except Exception as create_error:
                print(f"Erro ao criar profile padrao: {create_error}")

    except Exception as e:
        print(f"Erro geral: {e}")

    return None

def create_test_prompts(supabase, user_id):
    """Create test prompts directly"""
    try:
        test_prompts = [
            {
                'user_id': user_id,
                'prompt_type': 'GENERAL',
                'name': 'general_config',
                'description': 'General code analysis prompt',
                'content': 'Analise o código fornecido considerando os seguintes criterios de qualidade...',
                'is_active': True,
                'is_default': False
            },
            {
                'user_id': user_id,
                'prompt_type': 'ARCHITECTURAL',
                'name': 'architectural_config',
                'description': 'Architecture-focused code analysis prompt',
                'content': 'Analise o código fornecido focusing on architectural principles...',
                'is_active': True,
                'is_default': False
            },
            {
                'user_id': user_id,
                'prompt_type': 'BUSINESS',
                'name': 'business_config',
                'description': 'Business logic focused code analysis prompt',
                'content': 'Analise o código fornecido focusing on business logic...',
                'is_active': True,
                'is_default': False
            }
        ]

        print("\nCriando prompts de teste...")
        for prompt in test_prompts:
            try:
                result = supabase.table('prompt_configurations').insert(prompt).execute()
                if result.data:
                    print(f"[OK] Criado: {prompt['name']} ({prompt['prompt_type']})")
                else:
                    print(f"[ERRO] Erro ao criar: {prompt['name']}")
            except Exception as e:
                print(f"[ERRO] Erro ao criar {prompt['name']}: {e}")

    except Exception as e:
        print(f"Erro ao criar prompts de teste: {e}")

def main():
    """Main function"""
    print("Verificando estrutura do Supabase...")

    try:
        supabase = create_supabase_client()
        print("Cliente Supabase criado com sucesso")

        # Check tables and create user if needed
        user_id = check_tables(supabase)

        if user_id:
            # Create test prompts
            create_test_prompts(supabase, user_id)
        else:
            print("Nao foi possivel criar usuario padrao")

            # Try to use a fixed UUID anyway
            default_uuid = "00000000-0000-0000-0000-000000000001"
            print(f"\nTentando usar UUID fixo: {default_uuid}")
            create_test_prompts(supabase, default_uuid)

        # Verify result
        print("\nVerificando prompts no Supabase...")
        try:
            result = supabase.table('prompt_configurations').select('*').execute()
            if result.data:
                print(f"Encontrados {len(result.data)} prompts:")
                for prompt in result.data:
                    print(f"   - ID: {prompt.get('id')}, Nome: {prompt.get('name')}, Tipo: {prompt.get('prompt_type')}")
            else:
                print("Nenhum prompt encontrado")
        except Exception as e:
            print(f"Erro ao verificar prompts: {e}")

    except Exception as e:
        print(f"Erro geral: {e}")

if __name__ == "__main__":
    main()