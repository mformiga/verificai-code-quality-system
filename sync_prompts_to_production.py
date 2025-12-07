#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para sincronizar prompts do PostgreSQL local para o Supabase/Render remoto
"""

import psycopg2
import os
from datetime import datetime

def get_postgres_local_prompts():
    """Obtém prompts do PostgreSQL local"""
    local_config = {
        'host': 'localhost',
        'port': '5432',
        'database': 'verificai',
        'user': 'verificai',
        'password': 'verificai123'
    }

    try:
        conn = psycopg2.connect(**local_config)
        cursor = conn.cursor()

        # Query para obter os melhores prompts (mesma lógica do app)
        query = """
        WITH ranked_prompts AS (
          SELECT prompt_type, content, updated_at, id, name, user_id,
                 ROW_NUMBER() OVER (
                   PARTITION BY prompt_type
                   ORDER BY
                     CASE WHEN id IN (7) THEN 1 ELSE 2 END ASC,
                     CASE WHEN name LIKE '%Template%' THEN 1 ELSE 2 END ASC,
                     LENGTH(content) DESC,
                     updated_at DESC
                 ) as rn
          FROM prompt_configurations
          WHERE is_active = true
        )
        SELECT prompt_type, content, updated_at, id, name
        FROM ranked_prompts
        WHERE rn = 1
        """

        cursor.execute(query)
        rows = cursor.fetchall()

        prompts = {}
        for row in rows:
            prompt_type, content, updated_at, prompt_id, name = row
            prompts[prompt_type.lower()] = {
                'content': content,
                'name': name,
                'updated_at': updated_at,
                'id': prompt_id
            }

        cursor.close()
        conn.close()
        return prompts

    except Exception as e:
        print(f"Erro ao obter prompts do PostgreSQL local: {e}")
        return {}

def sync_to_render_postgres():
    """Sincroniza prompts para o PostgreSQL remoto no Render"""

    # Configuração do PostgreSQL remoto (Render)
    # Você precisará obter essas credenciais do dashboard do Render
    remote_config = {
        'host': 'dpg-d4p4s5re5dus7381mdug-a.virginia-postgres.render.com',  # Exemplo - substitua pelo real
        'port': '5432',
        'database': 'verificai',
        'user': 'verificai_user',
        'password': 'sua_senha_aqui'  # Você precisará obter do dashboard
    }

    # Obter prompts do local
    local_prompts = get_postgres_local_prompts()

    if not local_prompts:
        print("Nenhum prompt encontrado no PostgreSQL local!")
        return False

    print(f"Encontrados {len(local_prompts)} prompts para sincronizar:")
    for prompt_type, prompt_data in local_prompts.items():
        print(f"  - {prompt_type}: {prompt_data['name']} ({len(prompt_data['content'])} chars)")

    # Para este script, vamos apenas mostrar o que seria sincronizado
    # A sincronização real requer as credenciais do Render PostgreSQL
    print("\n=== PROMPTS PARA SINCRONIZAR ===")
    print("Para completar a sincronização manualmente:")
    print("1. Acesse o dashboard do Render")
    print("2. Vá para o PostgreSQL instance 'avalia-db'")
    print("3. Use o Query Editor ou conecte via psql")
    print("4. Execute os inserts abaixo:")

    for prompt_type, prompt_data in local_prompts.items():
        print(f"\n-- Prompt: {prompt_type.upper()}")
        print(f"INSERT INTO prompt_configurations (prompt_type, name, content, user_id, is_active, is_default, created_at, updated_at, created_by, updated_by)")
        print(f"VALUES ('{prompt_type.upper()}', '{prompt_data['name']}', $${prompt_data['content']}$$, 1, true, false, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 1, 1);")
        print("ON CONFLICT (prompt_type, name) DO UPDATE SET")
        print("  content = EXCLUDED.content,")
        print("  updated_at = CURRENT_TIMESTAMP;")

    return True

def prepare_production_secrets():
    """Prepara as configurações para produção no Streamlit"""

    print("\n=== CONFIGURAÇÕES PARA STREAMLIT CLOUD ===")
    print("Adicione estes secrets no seu app Streamlit Cloud:")
    print("\n[secrets.toml]")
    print("# Configuração Supabase/Render PostgreSQL")
    print("POSTGRES_HOST = \"dpg-d4p4s5re5dus7381mdug-a.virginia-postgres.render.com\"")
    print("POSTGRES_PORT = \"5432\"")
    print("POSTGRES_DB = \"verificai\"")
    print("POSTGRES_USER = \"verificai_user\"")
    print("POSTGRES_PASSWORD = \"sua_senha_aqui\"  # Obter do dashboard Render")
    print("ENVIRONMENT = \"production\"")

    print("\n# OU se quiser usar Supabase")
    print("SUPABASE_URL = \"https://seu-project.supabase.co\"")
    print("SUPABASE_SERVICE_ROLE_KEY = \"sua_chave_aqui\"")

if __name__ == "__main__":
    print("=== SINCRONIZAÇÃO DE PROMPTS PARA PRODUÇÃO ===\n")

    # Obter prompts locais
    prompts = get_postgres_local_prompts()

    if prompts:
        print(f"[OK] {len(prompts)} prompts encontrados no PostgreSQL local:")
        for prompt_type, data in prompts.items():
            print(f"  - {prompt_type}: {data['name']} ({len(data['content'])} chars)")

        # Mostrar script de sincronização
        sync_to_render_postgres()

        # Preparar configurações para produção
        prepare_production_secrets()

        print(f"\n=== PROXIMOS PASSOS ===")
        print("1. Execute os inserts SQL no PostgreSQL remoto (Render)")
        print("2. Configure as variaveis de ambiente no Streamlit Cloud")
        print("3. Faça push para GitHub e deploy automaticamente")

    else:
        print("[ERRO] Nenhum prompt encontrado para sincronizar")