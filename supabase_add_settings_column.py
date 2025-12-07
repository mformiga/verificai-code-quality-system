#!/usr/bin/env python3
"""
Add settings column to prompt_configurations table in Supabase
"""

import os
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

def check_table_structure(supabase):
    """Check current table structure"""
    try:
        # Try to insert a test record with settings
        test_data = {
            'user_id': 1,
            'prompt_type': 'GENERAL',
            'name': 'test_structure',
            'content': 'test content',
            'settings': {}
        }

        result = supabase.table('prompt_configurations').insert(test_data).execute()
        return True
    except Exception as e:
        error_msg = str(e)
        if 'settings' in error_msg:
            print("Coluna 'settings' nao encontrada na tabela")
            return False
        else:
            print(f"Outro erro: {error_msg}")
            return True

def add_settings_column():
    """Generate SQL to add settings column"""

    sql = """
-- Adicionar coluna settings na tabela prompt_configurations
ALTER TABLE prompt_configurations
ADD COLUMN IF NOT EXISTS settings JSONB DEFAULT '{}';

-- Criar index para a coluna settings (opcional)
CREATE INDEX IF NOT EXISTS idx_prompt_configurations_settings ON prompt_configurations USING GIN(settings);

-- Atualizar registros existentes com settings vazio
UPDATE prompt_configurations
SET settings = '{}'
WHERE settings IS NULL;

-- Verificar a estrutura da tabela
\\d prompt_configurations;

-- Verificar os dados
SELECT COUNT(*) as total_records FROM prompt_configurations;
SELECT user_id, prompt_type, name, settings FROM prompt_configurations LIMIT 5;
"""

    print("SQL para adicionar a coluna 'settings' (execute no SQL Editor do Supabase):")
    print("=" * 80)
    print(sql)
    print("=" * 80)

    return sql

def main():
    """Main function"""
    print("Verificando estrutura da tabela prompt_configurations no Supabase...")

    try:
        supabase = create_supabase_client()
        print("Cliente Supabase criado com sucesso")

        # Check current structure
        print("\nVerificando se coluna 'settings' existe...")
        if check_table_structure(supabase):
            print("Coluna 'settings' ja existe ou tabela esta funcional")
        else:
            print("Coluna 'settings' nao encontrada")
            print("\nE necessario executar o SQL abaixo no SQL Editor do Supabase:")
            add_settings_column()

    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    main()