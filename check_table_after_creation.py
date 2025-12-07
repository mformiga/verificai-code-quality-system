#!/usr/bin/env python3
"""
Script para verificar se a tabela source_codes foi criada corretamente
Execute este script após rodar o SQL manualmente no painel do Supabase
"""

import os
import time
from dotenv import load_dotenv
from supabase import create_client
import sys

# Carregar variáveis de ambiente
load_dotenv('.env.supabase')

# Configurações do Supabase
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    print("[!] Erro: Variáveis de ambiente do Supabase não encontradas")
    print("Verifique o arquivo .env.supabase")
    sys.exit(1)

# Criar cliente Supabase
print("[*] Conectando ao Supabase...")
try:
    supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
    print("[+] Conectado com sucesso!")
except Exception as e:
    print(f"[!] Erro ao conectar: {str(e)}")
    sys.exit(1)

print("\n" + "=" * 60)
print("[*] VERIFICANDO TABELA SOURCE_CODES")
print("=" * 60)

# 1. Verificar se a tabela é acessível via API REST
print("\n[1] Testando acesso à tabela via API REST...")
try:
    # Tentar um SELECT simples
    response = supabase.table('source_codes').select('*').limit(0).execute()

    if hasattr(response, 'data') and response.data is not None:
        print("[+] SUCESSO! Tabela source_codes é acessível via API REST!")
    else:
        print("[!] Tabela não acessível")

except Exception as e:
    error_str = str(e).lower()
    if 'not found' in error_str or 'does not exist' in error_str:
        print("[!] Tabela source_codes não foi encontrada")
        print("\n    Execute o SQL manualmente:")
        print("    1. Acesse: https://app.supabase.com/project/jjxmfidggofuaxcdtkrd")
        print("    2. Vá para 'SQL Editor'")
        print("    3. Cole e execute o conteúdo do arquivo supabase_manual_setup.sql")
    else:
        print(f"[!] Erro: {str(e)}")

# 2. Se a tabela existe, tentar inserir um registro de teste
print("\n[2] Testando inserção de registro...")
try:
    test_record = {
        'code_id': 'test_verification_' + str(int(time.time())),
        'title': 'Teste de Verificação',
        'description': 'Registro de teste para verificar se a tabela funciona',
        'content': 'function hello() { console.log("Hello, World!"); }',
        'file_name': 'test.js',
        'file_extension': 'js',
        'programming_language': 'javascript',
        'line_count': 1,
        'character_count': 45,
        'size_bytes': 45
    }

    response = supabase.table('source_codes').insert(test_record).execute()

    if hasattr(response, 'data') and response.data:
        inserted_id = response.data[0].get('id')
        print(f"[+] SUCESSO! Registro inserido com ID: {inserted_id}")

        # Tentar ler de volta
        print("\n[3] Testando leitura do registro inserido...")
        read_response = supabase.table('source_codes').select('*').eq('code_id', test_record['code_id']).execute()

        if hasattr(read_response, 'data') and read_response.data:
            print("[+] SUCESSO! Registro lido com sucesso")
            record = read_response.data[0]
            print(f"    - Título: {record.get('title')}")
            print(f"    - Status: {record.get('status')}")
            print(f"    - Criado em: {record.get('created_at')}")

            # Limpar registro de teste
            print("\n[4] Limpando registro de teste...")
            delete_response = supabase.table('source_codes').delete().eq('code_id', test_record['code_id']).execute()
            print("[+] Registro de teste removido")

        else:
            print("[!] Erro ao ler registro inserido")

    else:
        print("[!] Erro ao inserir registro de teste")

except Exception as e:
    print(f"[!] Erro no teste de inserção: {str(e)}")

# 3. Verificar estrutura da tabela (se possível)
print("\n[5] Verificando estrutura da tabela...")
print("\nEstrutura esperada da tabela source_codes:")
print("-" * 60)
print("""
Colunas:
- id: UUID (Primary Key, auto-generated)
- code_id: VARCHAR(255) UNIQUE NOT NULL
- title: VARCHAR(255) NOT NULL
- description: TEXT
- content: TEXT NOT NULL
- file_name: VARCHAR(255) NOT NULL
- file_extension: VARCHAR(50) NOT NULL
- programming_language: VARCHAR(100)
- line_count: INTEGER
- character_count: INTEGER
- size_bytes: BIGINT
- status: VARCHAR(50) DEFAULT 'active'
- is_public: BOOLEAN DEFAULT false
- is_processed: BOOLEAN DEFAULT false
- processing_status: VARCHAR(50) DEFAULT 'pending'
- user_id: UUID (FK para auth.users)
- created_at: TIMESTAMP WITH TIME ZONE DEFAULT NOW()
- updated_at: TIMESTAMP WITH TIME ZONE DEFAULT NOW()

Recursos adicionais:
- Row Level Security (RLS) habilitado
- Índices em code_id, status, e user_id
- Trigger para atualizar updated_at automaticamente
- Políticas de segurança para acesso por usuário
""")

print("\n" + "=" * 60)
print("[+] VERIFICAÇÃO CONCLUÍDA")
print("=" * 60)

import time
print(f"\nData/Hora da verificação: {time.strftime('%Y-%m-%d %H:%M:%S')}")

# Resumo final
print("\n[+] RESUMO:")
print("1. Execute o SQL do arquivo supabase_manual_setup.sql no painel do Supabase")
print("2. Execute este script novamente para verificar se a tabela foi criada")
print("3. Se tudo estiver correto, a tabela está pronta para uso pela aplicação")

print("\n[+] URL do projeto Supabase:")
print("    https://app.supabase.com/project/jjxmfidggofuaxcdtkrd")

print("\n[+] Próximos passos:")
print("1. Verifique se o backend consegue usar a tabela")
print("2. Teste o upload de arquivos de código")
print("3. Verifique se o streamlit consegue ler os registros")