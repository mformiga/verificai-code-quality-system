#!/usr/bin/env python3
"""Teste simples para verificar conexão com Supabase"""

import os
from supabase import create_client

# Configuração
SUPABASE_URL = "https://jjxmfidggofuaxcdtkrd.supabase.co"
# Cole sua service_role_key aqui
SUPABASE_KEY = "COLE_A_CHAVE_AQUI"

print("Testando conexão com Supabase...")
print(f"URL: {SUPABASE_URL}")
print(f"Key: {SUPABASE_KEY[:20]}..." if SUPABASE_KEY != "COLE_A_CHAVE_AQUI" else "Key não configurada")

if SUPABASE_KEY == "COLE_A_CHAVE_AQUI":
    print("\nERRO: Configure a SERVICE_ROLE_KEY no arquivo")
    exit(1)

try:
    # Conectar
    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("\n✅ Conexão bem-sucedida!")

    # Testar tabela de prompts (funciona)
    print("\nTestando tabela prompt_configurations...")
    response = client.table('prompt_configurations').select('*').limit(1).execute()
    print(f"Status: {len(response.data) if response.data else 0} registros encontrados")

    # Testar tabela de source_codes (pode dar erro)
    print("\nTestando tabela source_codes...")
    try:
        response = client.table('source_codes').select('*').limit(1).execute()
        print(f"Status: {len(response.data) if response.data else 0} registros encontrados")

        # Se não tem dados, tentar inserir um teste
        if not response.data:
            print("\nTentando inserir um registro de teste...")
            test_data = {
                'code_id': 'test_123',
                'title': 'Teste',
                'content': 'print("teste")',
                'file_name': 'teste.py',
                'file_extension': '.py',
                'programming_language': 'Python'
            }
            response = client.table('source_codes').insert(test_data).execute()
            print("✅ Inserção bem-sucedida!")

    except Exception as e:
        print(f"❌ Erro ao acessar source_codes: {e}")

        # Se a tabela não existe, mostrar como criar
        if "does not exist" in str(e) or "relation" in str(e).lower():
            print("\n⚠️ A tabela source_codes não existe!")
            print("Execute o SQL do arquivo supabase_setup.sql no Supabase")

except Exception as e:
    print(f"\n❌ Erro na conexão: {e}")
    if "Invalid API key" in str(e):
        print("\nSolução: Verifique se está usando a SERVICE_ROLE_KEY (não a ANON_KEY)")