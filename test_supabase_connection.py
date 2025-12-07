#!/usr/bin/env python3
"""
Teste de Conexão com Supabase
Usa o project_ref jjxmfidggofuaxcdtkrd
"""

import os
import sys
from pathlib import Path

def load_env():
    """Carrega variáveis de ambiente"""
    env_file = Path(".env.supabase")
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
        print("✅ Variáveis de ambiente carregadas de .env.supabase")
        return True
    else:
        print("❌ Arquivo .env.supabase não encontrado")
        return False

def test_supabase_imports():
    """Testa se consegue importar bibliotecas Supabase"""
    try:
        from supabase import create_client, Client
        print("✅ Biblioteca supabase importada com sucesso")
        return True
    except ImportError as e:
        print(f"❌ Erro ao importar supabase: {e}")
        print("💡 Instale com: pip install supabase")
        return False

def test_basic_connection():
    """Testa conexão básica com Supabase"""
    try:
        from supabase import create_client

        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_ANON_KEY")

        if not url or not key:
            print("❌ SUPABASE_URL ou SUPABASE_ANON_KEY não encontrados")
            return False

        print(f"🔗 Conectando ao URL: {url}")
        print(f"🔑 Usando anon key: {key[:20]}...")

        client = create_client(url, key)
        print("✅ Cliente Supabase criado com sucesso")
        return client

    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        return None

def test_database_schema(client):
    """Testa se as tabelas do schema existem"""
    try:
        expected_tables = [
            'profiles',
            'analyses',
            'analysis_results',
            'uploaded_files',
            'test_connection'
        ]

        print("\n📊 Verificando tabelas no banco:")

        for table in expected_tables:
            try:
                # Testa se consegue fazer SELECT na tabela
                response = client.table(table).select('count', count='exact').execute()
                count = response.count if hasattr(response, 'count') else 'N/A'
                print(f"✅ {table}: {count} registros")
            except Exception as e:
                print(f"❌ {table}: Erro - {str(e)[:50]}...")

    except Exception as e:
        print(f"❌ Erro ao verificar schema: {e}")

def test_storage_access(client):
    """Testa acesso aos buckets de storage"""
    try:
        expected_buckets = [
            'code-files',
            'analysis-reports',
            'user-avatars'
        ]

        print("\n📁 Verificando storage buckets:")

        for bucket in expected_buckets:
            try:
                # Testa listagem de arquivos
                response = client.storage.from_(bucket).list()
                print(f"✅ {bucket}: {len(response)} arquivos")
            except Exception as e:
                print(f"❌ {bucket}: Erro - {str(e)[:50]}...")

    except Exception as e:
        print(f"❌ Erro ao verificar storage: {e}")

def generate_config_file():
    """Gera arquivo de configuração para Streamlit Cloud"""
    config_content = '''# Cole estas configurações no Streamlit Cloud → Settings → Secrets

[supabase]
SUPABASE_URL = "https://jjxmfidggofuaxcdtkrd.supabase.co"
SUPABASE_ANON_KEY = "SUA_ANON_KEY_AQUI"
SUPABASE_SERVICE_ROLE_KEY = "SUA_SERVICE_ROLE_KEY_AQUI"
SUPABASE_PROJECT_REF = "jjxmfidggofuaxcdtkrd"

[database]
DATABASE_URL = "postgresql://postgres.iamuser:SUA_SENHA@aws-0-us-east-1.pooler.supabase.com:5432/postgres"
'''

    with open("streamlit_cloud_secrets.txt", 'w') as f:
        f.write(config_content)

    print("✅ Arquivo 'streamlit_cloud_secrets.txt' criado com seu project_ref")

def main():
    """Função principal"""
    print("Teste de Conexão com Supabase")
    print("=" * 40)
    print("Project: jjxmfidggofuaxcdtkrd")
    print("=" * 40)

    # Carrega ambiente
    if not load_env():
        return False

    # Mostra configuração atual
    print("\n⚙️ Configuração atual:")
    print(f"URL: {os.getenv('SUPABASE_URL')}")
    print(f"Project Ref: {os.getenv('SUPABASE_PROJECT_REF')}")

    # Testa imports
    if not test_supabase_imports():
        return False

    # Testa conexão
    client = test_basic_connection()
    if not client:
        return False

    # Testa schema
    test_database_schema(client)

    # Testa storage
    test_storage_access(client)

    # Gera config
    generate_config_file()

    print("\n🎯 Próximos passos:")
    print("1. Obtenha suas chaves em: https://app.supabase.com/project/jjxmfidggofuaxcdtkrd/settings/api")
    print("2. Atualize .env.supabase com suas chaves reais")
    print("3. Execute este script novamente para testar")
    print("4. Configure secrets no Streamlit Cloud usando streamlit_cloud_secrets.txt")

    return True

if __name__ == "__main__":
    try:
        success = main()
        print(f"\n{'✅ Sucesso!' if success else '❌ Falha!'}")
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Teste cancelado")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        sys.exit(1)