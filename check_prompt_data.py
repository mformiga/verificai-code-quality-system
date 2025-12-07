#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificar dados na tabela prompt_configurations do Supabase
"""

import os
from supabase import create_client
import json

def load_supabase_config():
    """Carrega configuracao do Supabase"""
    env_file = ".env.supabase"

    with open(env_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    config = {}
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            key, value = line.split('=', 1)
            config[key] = value

    return config

def check_prompt_data():
    """Verifica dados na tabela prompt_configurations"""

    config = load_supabase_config()
    client = create_client(config['SUPABASE_URL'], config['SUPABASE_SERVICE_ROLE_KEY'])

    print("Verificando dados em prompt_configurations...")
    print("=" * 50)

    try:
        # Obter todos os dados
        response = client.table('prompt_configurations').select('*').execute()

        if response.data:
            print(f"Total de registros: {len(response.data)}")
            print("\nDados:")

            for i, record in enumerate(response.data, 1):
                print(f"\n--- Registro {i} ---")
                print(f"ID: {record.get('id')}")
                print(f"Prompt ID: {record.get('prompt_id')}")
                print(f"Nome: {record.get('name')}")
                print(f"Config Name: {record.get('config_name')}")
                print(f"Tipo: {record.get('prompt_type')}")
                print(f"Descricao: {record.get('description')}")
                print(f"Ativo: {record.get('is_active')}")
                print(f"Default: {record.get('is_default')}")
                print(f"User ID: {record.get('user_id')}")

                # Exibe o conteúdo formatado
                content = record.get('content')
                if content:
                    print(f"Conteudo (primeiros 200 chars): {content[:200]}...")
                    if len(content) > 200:
                        print(f"[Conteudo completo tem {len(content)} caracteres]")

                # Exibe variáveis se existir
                variables = record.get('variables')
                if variables:
                    print(f"Variaveis: {variables}")

                print(f"Criado em: {record.get('created_at')}")
                print(f"Atualizado em: {record.get('updated_at')}")
        else:
            print("Nenhum registro encontrado")

        print("\n" + "=" * 50)
        print("VERIFICACAO DE TABELAS RELACIONADAS:")
        print("-" * 50)

        # Verificar se existe tabela para armazenar codigos fonte
        tables_to_check = ['file_paths', 'analyses', 'analysis_results']

        for table in tables_to_check:
            try:
                response = client.table(table).select('count', count='exact').limit(1).execute()
                count = response.count if hasattr(response, 'count') else 0
                print(f"{table}: {count} registros")
            except:
                print(f"{table}: NAO existe")

        return True

    except Exception as e:
        print(f"ERRO: {e}")
        return False

if __name__ == "__main__":
    check_prompt_data()