#!/usr/bin/env python3
"""
Import prompts from Supabase to local PostgreSQL database
"""

import psycopg2
import os
from supabase_client import get_supabase_client
from datetime import datetime

# PostgreSQL configuration
POSTGRES_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': os.getenv('POSTGRES_PORT', '5432'),
    'database': os.getenv('POSTGRES_DB', 'verificai'),
    'user': os.getenv('POSTGRES_USER', 'verificai'),
    'password': os.getenv('POSTGRES_PASSWORD', 'verificai123')
}

def import_prompts_from_supabase():
    """Import prompts from Supabase to local PostgreSQL"""
    try:
        print("Connecting to Supabase...")
        supabase = get_supabase_client()

        # Get all prompts from Supabase
        response = supabase.client.table('prompts').select('*').execute()

        if not response.data:
            print("No prompts found in Supabase")
            return False

        print(f"Found {len(response.data)} prompts in Supabase")

        # Connect to PostgreSQL
        print("Connecting to PostgreSQL...")
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        cursor = conn.cursor()

        imported_count = 0

        for prompt_data in response.data:
            prompt_type = prompt_data.get('type', 'general')
            content = prompt_data.get('content', '')
            version = prompt_data.get('version', 1)
            created_at = prompt_data.get('created_at', datetime.now())
            updated_at = prompt_data.get('updated_at', datetime.now())

            # Convert to uppercase for PostgreSQL enum
            prompt_type_upper = prompt_type.upper()

            # Check if prompt already exists
            cursor.execute("SELECT id FROM prompts WHERE type = %s AND user_id = 1", (prompt_type_upper,))
            existing = cursor.fetchone()

            if existing:
                print(f"Prompt '{prompt_type_upper}' already exists, updating...")
                cursor.execute("""
                    UPDATE prompts
                    SET content = %s, version = %s, updated_at = %s
                    WHERE id = %s
                """, (content, version, updated_at, existing[0]))
            else:
                print(f"Importing prompt '{prompt_type_upper}'...")
                cursor.execute("""
                    INSERT INTO prompts (type, content, version, user_id, created_at, updated_at, created_by, updated_by)
                    VALUES (%s, %s, %s, 1, %s, %s, 1, 1)
                """, (prompt_type_upper, content, version, created_at, updated_at))

            imported_count += 1

        # Commit transaction
        conn.commit()
        conn.close()

        print(f"Successfully imported {imported_count} prompts to PostgreSQL")
        return True

    except Exception as e:
        print(f"Error importing prompts: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

def create_default_prompts():
    """Create default prompts if no prompts exist in Supabase"""
    print("Creating default prompts...")

    default_prompts = {
        "general": """Analise o código fornecido considerando os seguintes critérios de qualidade:
1. **Princípios SOLID**: Verifique violações do Single Responsibility Principle e Dependency Inversion
2. **Acoplamento a Frameworks**: Detecte dependências excessivas de frameworks específicos
3. **Violação de Camadas**: Identifique lógica de negócio em camadas de interface
4. **Gerenciamento de Recursos**: Verifique liberação adequada de recursos externos
5. **Tratamento de Erros**: Analise blocos de exceção e tratamento de erros

Para cada critério, indique:
- Status: ✅ Conforme ou ❌ Não conforme
- Descrição detalhada dos problemas encontrados
- Recomendações específicas de correção
- Linhas de código afetadas""",

        "architectural": """Analise a conformidade arquitetural do código fornecido:
1. **Padrões de Projeto**: Verifique o uso adequado de padrões de projeto (Factory, Observer, Strategy, etc.)
2. **Arquitetura em Camadas**: Confirme a separação adequada entre camadas (UI, Service, Data)
3. **Injeção de Dependências**: Verifique a implementação correta de DI
4. **API Design**: Analise a consistência e boas práticas nas APIs
5. **Configuração e Segregação**: Verifique separação entre configuração e lógica de negócio

Avalie:
- Conformidade com padrões arquiteturais definidos
- Impacto das violações na manutenibilidade
- Sugestões de refatoração arquitetural
- Riscos técnicos identificados""",

        "business": """Analise a conformidade do código com regras de negócio:
1. **Validações de Negócio**: Verifique implementação de regras de negócio específicas
2. **Tratamento de Dados Sensíveis**: Confirme proteção adequada de dados críticos
3. **Auditoria e Logging**: Verifique registro de eventos de negócio importantes
4. **Cálculos e Fórmulas**: Valide precisão de cálculos de negócio
5. **Fluxos de Autorização**: Analise implementação de regras de acesso

Para cada regra de negócio:
- Status de conformidade
- Impacto no negócio em caso de violação
- Recomendações de correção
- Níveis de risco associados"""
    }

    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        cursor = conn.cursor()

        for prompt_type, content in default_prompts.items():
            prompt_type_upper = prompt_type.upper()
            print(f"Creating default prompt: {prompt_type_upper}")

            # Check if prompt already exists
            cursor.execute("SELECT id FROM prompts WHERE type = %s AND user_id = 1", (prompt_type_upper,))
            existing = cursor.fetchone()

            if existing:
                # Update existing prompt
                cursor.execute("""
                    UPDATE prompts
                    SET content = %s, version = version + 1, updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, (content, existing[0]))
                print(f"Updated existing prompt: {prompt_type_upper}")
            else:
                # Insert new prompt
                cursor.execute("""
                    INSERT INTO prompts (type, content, version, user_id, created_at, updated_at, created_by, updated_by)
                    VALUES (%s, %s, 1, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 1, 1)
                """, (prompt_type_upper, content))
                print(f"Created new prompt: {prompt_type_upper}")

        conn.commit()
        conn.close()

        print("Default prompts created successfully!")
        return True

    except Exception as e:
        print(f"Error creating default prompts: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    print("Starting prompt import from Supabase to PostgreSQL...")

    # Try to import from Supabase first
    if not import_prompts_from_supabase():
        print("Import from Supabase failed, creating default prompts...")
        create_default_prompts()

    print("Import process completed!")