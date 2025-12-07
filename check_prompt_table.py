#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar a tabela prompt_configurations no Supabase
"""

import os
import sys
import psycopg2

# Configurar saída para UTF-8 no Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
from psycopg2.extras import DictCursor
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def get_supabase_connection():
    """Obter conexão com o Supabase"""
    try:
        # Obter URL do Supabase das variáveis de ambiente
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')

        if not supabase_url:
            # Tentar obter do arquivo .streamlit/secrets.toml
            try:
                import toml
                with open('.streamlit/secrets.toml', 'r') as f:
                    secrets = toml.load(f)
                    supabase_url = secrets.get('SUPABASE_URL')
                    supabase_key = secrets.get('SUPABASE_KEY')
            except:
                pass

        if not supabase_url:
            # Tentar obter das variáveis de ambiente do arquivo secrets
            supabase_url = os.getenv('supabase_url')
            supabase_key = os.getenv('supabase_key')

        if not supabase_url:
            print("❌ Não foi possível encontrar a URL do Supabase")
            return None

        # Extrair detalhes da conexão da URL do Supabase
        # Formato: postgresql://postgres:[password]@host:port/postgres
        if supabase_url.startswith('postgresql://'):
            return psycopg2.connect(supabase_url)
        else:
            # Converter URL do Supabase para formato PostgreSQL
            if '://postgres:' in supabase_url:
                db_url = supabase_url.replace('postgres://', 'postgresql://')
                return psycopg2.connect(db_url)
            else:
                print(f"❌ URL do Supabase em formato desconhecido: {supabase_url}")
                return None

    except Exception as e:
        print(f"❌ Erro ao conectar ao Supabase: {e}")
        return None

def check_prompt_configurations():
    """Verificar a tabela prompt_configurations"""
    conn = get_supabase_connection()
    if not conn:
        print("❌ Falha na conexão com o banco de dados")
        return

    try:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            # 1. Verificar se a tabela existe
            print("\n🔍 Verificando estrutura da tabela prompt_configurations...")
            cur.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = 'prompt_configurations'
                ORDER BY ordinal_position;
            """)

            columns = cur.fetchall()
            if not columns:
                print("❌ Tabela 'prompt_configurations' não encontrada")
                return

            print("\n📋 Estrutura da tabela prompt_configurations:")
            for col in columns:
                print(f"  - {col['column_name']}: {col['data_type']} "
                      f"({'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'})")

            # 2. Contar registros
            print("\n🔢 Contando registros...")
            cur.execute("SELECT COUNT(*) as total FROM prompt_configurations")
            total = cur.fetchone()['total']
            print(f"   Total de registros: {total}")

            # 3. Listar todos os registros
            print("\n📝 Listando todos os registros...")
            cur.execute("""
                SELECT
                    id,
                    user_id,
                    prompt_type,
                    name,
                    description,
                    is_active,
                    is_default,
                    created_at,
                    updated_at
                FROM prompt_configurations
                ORDER BY updated_at DESC
            """)

            registros = cur.fetchall()

            if not registros:
                print("   ⚠️ Nenhum registro encontrado")
            else:
                print(f"\n📋 Encontrados {len(registros)} registros:\n")
                for reg in registros:
                    print(f"🔹 ID: {reg['id']}")
                    print(f"   User ID: {reg['user_id']}")
                    print(f"   Tipo: {reg['prompt_type']}")
                    print(f"   Nome: {reg['name']}")
                    print(f"   Descrição: {reg['description']}")
                    print(f"   Ativo: {reg['is_active']}")
                    print(f"   Default: {reg['is_default']}")
                    print(f"   Criado: {reg['created_at']}")
                    print(f"   Atualizado: {reg['updated_at']}")
                    print()

            # 4. Mostrar conteúdo completo dos prompts
            print("\n📄 Conteúdo completo dos prompts:")
            cur.execute("""
                SELECT
                    id,
                    prompt_type,
                    name,
                    LEFT(content, 500) as content_preview,
                    LENGTH(content) as content_length,
                    settings
                FROM prompt_configurations
                WHERE content IS NOT NULL AND content != ''
                ORDER BY prompt_type, updated_at DESC
            """)

            prompts = cur.fetchall()

            if not prompts:
                print("   ⚠️ Nenhum prompt com conteúdo encontrado")
            else:
                for prompt in prompts:
                    print(f"\n" + "="*80)
                    print(f"🔹 ID: {prompt['id']}")
                    print(f"   Tipo: {prompt['prompt_type']}")
                    print(f"   Nome: {prompt['name']}")
                    print(f"   Tamanho do conteúdo: {prompt['content_length']} caracteres")
                    print(f"   Settings: {prompt['settings']}")

                    # Obter o conteúdo completo
                    cur.execute("""
                        SELECT content FROM prompt_configurations WHERE id = %s
                    """, (prompt['id'],))
                    full_content = cur.fetchone()['content']

                    print(f"\n📝 Conteúdo completo:")
                    print("-"*40)
                    print(full_content)
                    print("-"*40)

            # 5. Verificar prompts por tipo
            print("\n📊 Resumo por tipo de prompt:")
            cur.execute("""
                SELECT
                    prompt_type,
                    COUNT(*) as count,
                    MAX(updated_at) as last_updated
                FROM prompt_configurations
                GROUP BY prompt_type
                ORDER BY prompt_type
            """)

            resumo = cur.fetchall()
            for r in resumo:
                print(f"   {r['prompt_type']}: {r['count']} registros (último: {r['last_updated']})")

    except Exception as e:
        print(f"❌ Erro durante a verificação: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    print("🔍 Verificando tabela prompt_configurations no Supabase...")
    print("="*60)
    check_prompt_configurations()