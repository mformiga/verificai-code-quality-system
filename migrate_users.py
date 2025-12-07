#!/usr/bin/env python3
"""
Migração de Usuários do Postgres Local para Supabase
"""

import os
import sys
import json
import hashlib
from pathlib import Path

def load_local_users():
    """Carrega usuários do banco local (simulado)"""
    # Você precisa ajustar isso para seu banco real
    # Este é um exemplo com dados simulados

    # Se você tem um arquivo JSON com usuários:
    users_file = Path("users.json")
    if users_file.exists():
        with open(users_file, 'r') as f:
            return json.load(f)

    # Dados exemplo - substitua pelos seus dados reais
    return [
        {
            "username": "admin",
            "email": "admin@example.com",
            "password_hash": "senha_hash_aqui",  # Você precisa ter os hashes
            "role": "admin",
            "full_name": "Administrator"
        },
        {
            "username": "teste",
            "email": "teste@example.com",
            "password_hash": "senha_hash_aqui",
            "role": "user",
            "full_name": "Usuário Teste"
        }
    ]

def load_supabase_config():
    """Carrega configuração do Supabase"""
    env_file = Path(".env.supabase")
    if not env_file.exists():
        print("ERRO: Arquivo .env.supabase não encontrado")
        return None

    with open(env_file, 'r') as f:
        content = f.read()
        for line in content:
            if line.strip() and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

    return {
        'url': os.getenv('SUPABASE_URL'),
        'service_key': os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    }

def migrate_to_supabase(users):
    """Migra usuários para Supabase"""
    try:
        from supabase import create_client

        config = load_supabase_config()
        if not config:
            return False

        client = create_client(config['url'], config['service_key'])
        print("✅ Conectado ao Supabase")

        migrated = 0
        for user in users:
            try:
                # Criar profile no Supabase
                profile_data = {
                    'username': user['username'],
                    'email': user['email'],
                    'full_name': user.get('full_name', ''),
                    'role': user.get('role', 'user')
                }

                # Nota: Você precisa ter os IDs dos auth.users
                # Isso é mais complexo porque o Supabase Auth não permite criar usuários com senhas diretamente via API

                print(f"⚠️ Usuário {user['username']} precisa ser criado manualmente no Supabase Auth")
                print(f"   Email: {user['email']}")
                print(f"   Role: {user['role']}")

                migrated += 1

            except Exception as e:
                print(f"❌ Erro ao migrar {user['username']}: {e}")

        return migrated

    except ImportError:
        print("❌ Biblioteca supabase não encontrada. Execute: pip install supabase")
        return False
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        return False

def create_manual_instructions(users):
    """Cria instruções para migração manual"""
    print("\n=== INSTRUÇÕES PARA MIGRAÇÃO MANUAL ===")
    print("\n1. Vá para: https://app.supabase.com/project/jjxmfidggofuaxcdtkrd/auth/users")
    print("2. Para cada usuário abaixo, clique em 'Add user':\n")

    for user in users:
        print(f"Usuário: {user['username']}")
        print(f"Email: {user['email']}")
        print(f"Role: {user.get('role', 'user')}")
        print(f"Full Name: {user.get('full_name', '')}")
        print("---")

def create_sql_inserts(users):
    """Cria inserts SQL para profiles (após criar auth.users)"""
    print("\n=== SQL PARA CRIAR PROFILES ===")
    print("Execute este SQL no Supabase SQL Editor após criar os usuários em Auth:")
    print("\n-- Você precisa pegar os IDs dos usuários criados em auth.users")

    for i, user in enumerate(users, 1):
        print(f"""
-- Para {user['username']} (substitua USER_ID pelo UUID real)
INSERT INTO public.profiles (id, username, full_name, role)
SELECT
    id,  -- ID do auth.users
    '{user['username']}',
    '{user.get('full_name', '')}',
    '{user.get('role', 'user')}'
FROM auth.users
WHERE email = '{user['email']}'
ON CONFLICT (id) DO UPDATE SET
    username = EXCLUDED.username,
    full_name = EXCLUDED.full_name,
    role = EXCLUDED.role;
""")

def main():
    print("🔄 MIGRAÇÃO DE USUÁRIOS - AVALIA")
    print("=" * 50)

    # Carregar usuários locais
    users = load_local_users()
    print(f"📋 Encontrados {len(users)} usuários para migrar")

    # Tentar migração automática
    print("\n🔍 Tentando migração...")
    migrated = migrate_to_supabase(users)

    # Criar instruções manuais
    create_manual_instructions(users)
    create_sql_inserts(users)

    print("\n📌 RESUMO:")
    print("1. Crie usuários manualmente no Supabase Auth")
    print("2. Execute os SQL inserts para os profiles")
    print("3. Remova funcionalidade de registro do app")
    print("4. Teste login com usuários existentes")

if __name__ == "__main__":
    main()