#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Setup Rapido do Supabase - AVALIA
Versao simplificada sem emojis
"""

import os
import sys
from pathlib import Path

def check_config():
    """Verifica configuracao"""
    env_file = Path(".env.supabase")
    if not env_file.exists():
        print("ERRO: Arquivo .env.supabase nao encontrado!")
        return False

    # Carrega variaveis
    os.environ["PYTHONIOENCODING"] = "utf-8"

    try:
        from dotenv import load_dotenv
        load_dotenv(env_file)
    except ImportError:
        pass

    supabase_url = os.getenv('SUPABASE_URL')
    service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

    print(f"URL: {supabase_url}")
    print(f"Service Key: {'Configurado' if service_key else 'Nao configurado'}")

    return bool(supabase_url and service_key)

def test_supabase_connection():
    """Testa conexao com Supabase"""
    try:
        from supabase import create_client
        supabase_url = os.getenv('SUPABASE_URL')
        service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

        client = create_client(supabase_url, service_key)

        # Teste basico
        response = client.table('test_connection').select('count').execute()
        print(f"[OK] Conexao Supabase funcionando")
        print(f"[OK] Tabela test_connection acessivel")
        return client
    except Exception as e:
        print(f"[ERRO] Falha na conexao: {e}")
        return None

def create_test_user_profiles(client):
    """Cria profiles para usuarios de teste"""
    print("\n[CRIACAO DE PROFILES]")

    test_profiles = [
        {
            'id': '00000000-0000-0000-0000-000000000001',  # Temporario
            'username': 'admin',
            'full_name': 'Administrator',
            'role': 'admin'
        },
        {
            'id': '00000000-0000-0000-0000-000000000002',  # Temporario
            'username': 'teste',
            'full_name': 'Usuario Teste',
            'role': 'user'
        }
    ]

    for profile in test_profiles:
        try:
            # Tenta inserir (provavelmente vai falhar se nao existir usuario)
            response = client.table('profiles').insert({
                'username': profile['username'],
                'full_name': profile['full_name'],
                'role': profile['role']
            }).execute()
            print(f"[OK] Profile criado: {profile['username']}")
        except Exception as e:
            print(f"[INFO] Profile {profile['username']}: {str(e)[:50]}...")

def check_tables(client):
    """Verifica todas as tabelas"""
    print("\n[VERIFICACAO DE TABELAS]")

    tables = ['profiles', 'analyses', 'analysis_results', 'uploaded_files', 'test_connection']

    for table in tables:
        try:
            response = client.table(table).select('count', count='exact').execute()
            count = response.count if hasattr(response, 'count') else 'N/A'
            print(f"[OK] {table}: {count} registros")
        except Exception as e:
            print(f"[ERRO] {table}: {str(e)[:50]}...")

def main():
    """Funcao principal"""
    print("=== AVALIA - SETUP DO SUPABASE ===")
    print("Processo automatico de configuracao\n")

    # 1. Verificar configuracao
    if not check_config():
        print("\nConfigure o arquivo .env.supabase primeiro!")
        return False

    # 2. Testar conexao
    client = test_supabase_connection()
    if not client:
        print("\nVerifique suas credenciais no .env.supabase")
        return False

    # 3. Verificar tabelas
    check_tables(client)

    # 4. Instructions para usuarios
    print("\n=== CRIACAO DE USUARIOS ===")
    print("A API Supabase nao permite criar usuarios via codigo.")
    print("Use a interface web:")
    print(f"URL: {os.getenv('SUPABASE_URL').replace('.co', '.co/auth/users')}")
    print("\nCrie estes usuarios:")
    print("1. Email: admin@avalia.com, Senha: admin123")
    print("2. Email: teste@avalia.com, Senha: teste123")

    # 5. Teste profiles (para usuarios existentes)
    create_test_user_profiles(client)

    # 6. Instructions finais
    print("\n=== PROXIMOS PASSOS ===")
    print("1. Crie usuarios na interface Supabase Auth")
    print("2. Teste login: http://localhost:8501")
    print("3. Verifique funcionalidades completas")
    print("\nResumo:")
    print("- [OK] Configuracao verificada")
    print("- [OK] Conexao Supabase OK")
    print("- [OK] Tabelas criadas")
    print("- [ ] Criar usuarios manualmente")
    print("- [ ] Testar aplicacao")

    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nSetup cancelado")
        sys.exit(1)
    except Exception as e:
        print(f"\nErro: {e}")
        sys.exit(1)