#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import psycopg2
from dotenv import load_dotenv

# Carregar variáveis de ambiente
if os.path.exists('.env.local'):
    load_dotenv('.env.local')
if os.path.exists('.env.supabase_local'):
    load_dotenv('.env.supabase_local')

POSTGRES_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': os.getenv('POSTGRES_PORT', '5432'),
    'database': os.getenv('POSTGRES_DB', 'verificai'),
    'user': os.getenv('POSTGRES_USER', 'verificai'),
    'password': os.getenv('POSTGRES_PASSWORD', 'verificai123')
}

def remover_tabela_prompts_seguro():
    print("=== REMOCAO SEGURA DA TABELA PROMPTS ===\n")

    try:
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        cursor = conn.cursor()

        # 1. Verificar conteúdo das tabelas dependentes
        print("1. Verificando conteudo das tabelas dependentes...")

        # Verificar prompt_history
        cursor.execute("SELECT COUNT(*) FROM prompt_history")
        count_history = cursor.fetchone()[0]
        print(f"   Registros em prompt_history: {count_history}")

        if count_history > 0:
            cursor.execute("SELECT prompt_id, COUNT(*) FROM prompt_history GROUP BY prompt_id")
            history_data = cursor.fetchall()
            print("   Distribuicao por prompt_id:")
            for row in history_data:
                print(f"     - Prompt ID {row[0]}: {row[1]} registros")

        # Verificar analyses
        cursor.execute("SELECT COUNT(*) FROM analyses")
        count_analyses = cursor.fetchone()[0]
        print(f"   Registros em analyses: {count_analyses}")

        if count_analyses > 0:
            cursor.execute("SELECT prompt_id, COUNT(*) FROM analyses GROUP BY prompt_id")
            analyses_data = cursor.fetchall()
            print("   Distribuicao por prompt_id:")
            for row in analyses_data:
                print(f"     - Prompt ID {row[0]}: {row[1]} registros")

        # 2. Verificar se há dados na tabela prompts
        cursor.execute("SELECT COUNT(*) FROM prompts")
        count_prompts = cursor.fetchone()[0]
        print(f"\n2. Registros na tabela prompts: {count_prompts}")

        # 3. Verificar se as tabelas dependentes realmente são usadas
        print("\n3. Analisando necessidade das tabelas dependentes...")

        # Se não houver dados nas tabelas dependentes, podemos remover as foreign keys e a tabela
        if count_history == 0 and count_analyses == 0:
            print("   Tabelas dependentes estao vazias - procedendo com remocao segura")

            # Remover foreign key da tabela prompt_history
            try:
                cursor.execute("""
                    ALTER TABLE prompt_history
                    DROP CONSTRAINT IF EXISTS prompt_history_prompt_id_fkey;
                """)
                print("   Foreign key removida de prompt_history")
            except Exception as e:
                print(f"   Aviso: Nao foi possivel remover FK de prompt_history: {str(e)}")

            # Remover foreign key da tabela analyses
            try:
                cursor.execute("""
                    ALTER TABLE analyses
                    DROP CONSTRAINT IF EXISTS analyses_prompt_id_fkey;
                """)
                print("   Foreign key removida de analyses")
            except Exception as e:
                print(f"   Aviso: Nao foi possivel remover FK de analyses: {str(e)}")

            # Remover a tabela prompts
            cursor.execute("DROP TABLE IF EXISTS prompts CASCADE;")
            print("   Tabela 'prompts' removida com sucesso!")

        else:
            print("   ATENCAO: Existem dados nas tabelas dependentes!")
            print("   Recomendacao:")
            print("   1. Fazer backup dos dados se necessario")
            print("   2. Remover ou atualizar os registros dependentes")
            print("   3. Depois remover a tabela prompts")

            # Opção 1: Remover colunas prompt_id das tabelas dependentes (se não forem mais usadas)
            resposta = input("\nDeseja remover as colunas prompt_id das tabelas dependentes? (s/n): ").lower()
            if resposta == 's':
                try:
                    # Remover coluna prompt_id de prompt_history
                    cursor.execute("ALTER TABLE prompt_history DROP COLUMN IF EXISTS prompt_id;")
                    print("   Coluna prompt_id removida de prompt_history")

                    # Remover coluna prompt_id de analyses
                    cursor.execute("ALTER TABLE analyses DROP COLUMN IF EXISTS prompt_id;")
                    print("   Coluna prompt_id removida de analyses")

                    # Agora pode remover a tabela prompts
                    cursor.execute("DROP TABLE IF EXISTS prompts CASCADE;")
                    print("   Tabela 'prompts' removida com sucesso!")

                except Exception as e:
                    print(f"   Erro ao remover colunas: {str(e)}")
            else:
                print("   Operacao cancelada. Nenhuma alteracao realizada.")

        # 4. Verificar estado final
        print("\n4. Verificando estado final...")
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public' AND table_name = 'prompts'
        """)
        if not cursor.fetchone():
            print("   ✓ Tabela 'prompts' nao existe mais")
        else:
            print("   ✗ Tabela 'prompts' ainda existe")

        cursor.execute("SELECT COUNT(*) FROM prompt_configurations")
        count_configs = cursor.fetchone()[0]
        print(f"   ✓ Tabela 'prompt_configurations' mantida com {count_configs} registros")

        conn.commit()
        cursor.close()
        conn.close()

        print("\n=== OPERACAO CONCLUIDA ===")

    except Exception as e:
        print(f"ERRO: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
            cursor.close()
            conn.close()

if __name__ == "__main__":
    remover_tabela_prompts_seguro()