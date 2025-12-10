#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para sincronizar prompts do Supabase remoto para PostgreSQL local
"""

import psycopg2
import os
import sys
from dotenv import load_dotenv
from supabase import create_client

# Configurar encoding para Windows
if sys.platform == 'win32':
    os.system('chcp 65001 > nul')

# Carregar variáveis de ambiente
load_dotenv('.env')
load_dotenv('.env.local')
load_dotenv('.env.supabase')

# Configuração PostgreSQL local
LOCAL_POSTGRES_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': os.getenv('POSTGRES_PORT', '5432'),
    'database': os.getenv('POSTGRES_DB', 'verificai'),
    'user': os.getenv('POSTGRES_USER', 'verificai'),
    'password': os.getenv('POSTGRES_PASSWORD', 'verificai123')
}

def sync_prompts_from_supabase():
    try:
        print("=" * 80)
        print("SINCRONIZANDO PROMPTS DO SUPABASE REMOTO PARA POSTGRESQL LOCAL")
        print("=" * 80)

        # Etapa 1: Obter prompts do Supabase
        print("1. Obtendo prompts do Supabase remoto...")
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

        supabase = create_client(supabase_url, supabase_key)
        response = supabase.table('prompt_configurations').select('*').execute()

        if not response.data:
            print("[ERRO] Nenhum prompt encontrado no Supabase!")
            return

        remote_prompts = response.data
        print(f"   Encontrados {len(remote_prompts)} prompts no Supabase")

        # Etapa 2: Conectar ao PostgreSQL local
        print("\n2. Conectando ao PostgreSQL local...")
        conn = psycopg2.connect(**LOCAL_POSTGRES_CONFIG)
        cursor = conn.cursor()

        # Etapa 3: Verificar prompts atuais no local
        cursor.execute("SELECT COUNT(*) FROM prompt_configurations")
        local_count = cursor.fetchone()[0]
        print(f"   Existem {local_count} prompts no PostgreSQL local")

        # Etapa 4: Remover todos os prompts locais
        if local_count > 0:
            print("\n3. Removendo prompts locais existentes...")
            cursor.execute("DELETE FROM prompt_configurations")
            deleted_rows = cursor.rowcount
            print(f"   Removidos {deleted_rows} prompts do PostgreSQL local")
        else:
            print("\n3. Nenhum prompt local para remover")

        # Etapa 5: Inserir prompts do Supabase
        print("\n4. Inserindo prompts do Supabase no PostgreSQL local...")
        inserted_count = 0

        for prompt in remote_prompts:
            try:
                # Preparar dados para inserção
                insert_query = """
                INSERT INTO prompt_configurations (
                    id, user_id, prompt_type, name, description, content,
                    is_active, is_default, created_at, updated_at,
                    created_by, updated_by
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                """

                values = (
                    prompt.get('id'),
                    prompt.get('user_id') if prompt.get('user_id') is not None else 1,  # Default user_id = 1 se for None
                    prompt.get('prompt_type'),
                    prompt.get('name'),
                    prompt.get('description'),
                    prompt.get('content'),
                    prompt.get('is_active', True),
                    prompt.get('is_default', False),
                    prompt.get('created_at'),
                    prompt.get('updated_at'),
                    prompt.get('created_by'),
                    prompt.get('updated_by')
                )

                cursor.execute(insert_query, values)
                inserted_count += 1

                print(f"   [OK] Inserido prompt ID {prompt.get('id')} - {prompt.get('prompt_type')}: {prompt.get('name')}")

            except Exception as insert_error:
                print(f"   [ERRO] Erro ao inserir prompt ID {prompt.get('id')}: {insert_error}")

        # Etapa 6: Confirmar transação
        conn.commit()
        print(f"\n   Total inseridos: {inserted_count} prompts")

        # Etapa 7: Verificação final
        print("\n5. Verificando sincronização...")
        cursor.execute("SELECT COUNT(*) FROM prompt_configurations")
        new_local_count = cursor.fetchone()[0]

        cursor.execute("""
            SELECT prompt_type, COUNT(*) as count
            FROM prompt_configurations
            GROUP BY prompt_type
            ORDER BY prompt_type
        """)
        type_counts = cursor.fetchall()

        print(f"   Total de prompts no PostgreSQL local: {new_local_count}")
        print("   Prompts por tipo:")
        for prompt_type, count in type_counts:
            print(f"     - {prompt_type}: {count}")

        # Etapa 8: Comparação final
        if new_local_count == len(remote_prompts):
            print("\n[OK] SINCRONIZACAO CONCLUIDA COM SUCESSO!")
            print(f"   {len(remote_prompts)} prompts do Supabase foram copiados para o PostgreSQL local")
        else:
            print(f"\n[AVISO] Contagem diferente!")
            print(f"   Supabase: {len(remote_prompts)} prompts")
            print(f"   PostgreSQL local: {new_local_count} prompts")

        # Mostrar detalhes finais
        print("\n" + "=" * 60)
        print("DETALHES DOS PROMPTS SINCRONIZADOS:")
        print("=" * 60)

        cursor.execute("""
            SELECT id, prompt_type, name, is_active, updated_at
            FROM prompt_configurations
            ORDER BY prompt_type, id
        """)

        for row in cursor.fetchall():
            prompt_id, prompt_type, name, is_active, updated_at = row
            status = "Ativo" if is_active else "Inativo"
            print(f"  ID {prompt_id} | {prompt_type} | {name} | {status} | {updated_at}")

        cursor.close()
        conn.close()

        print("\n" + "=" * 80)
        print("SINCRONIZAÇÃO FINALIZADA")
        print("=" * 80)

    except Exception as e:
        print(f"\n[ERRO] Durante a sincronização: {e}")
        if 'conn' in locals():
            conn.rollback()
            cursor.close()
            conn.close()

if __name__ == "__main__":
    sync_prompts_from_supabase()