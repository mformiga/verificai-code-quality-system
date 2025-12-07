#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Criar usuarios de teste diretamente no Supabase
"""

import os
import requests
import json
from pathlib import Path

def load_config():
    """Carrega configuracao"""
    env_file = Path(".env.supabase")
    if env_file.exists():
        from dotenv import load_dotenv
        load_dotenv(env_file)

    return {
        'url': os.getenv('SUPABASE_URL'),
        'anon_key': os.getenv('SUPABASE_ANON_KEY'),
        'service_key': os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    }

def create_users_via_api():
    """Tenta criar usuarios via API REST"""
    config = load_config()

    headers = {
        'apikey': config['service_key'],
        'Authorization': f'Bearer {config["service_key"]}',
        'Content-Type': 'application/json'
    }

    # URL da API de auth do Supabase
    auth_url = config['url'].replace('supabase.co', 'supabase.co/auth/v1/admin/users')

    users = [
        {
            'email': 'admin@avalia.com',
            'password': 'admin123',
            'email_confirm': True,
            'user_metadata': {
                'username': 'admin',
                'full_name': 'Administrator'
            }
        },
        {
            'email': 'teste@avalia.com',
            'password': 'teste123',
            'email_confirm': True,
            'user_metadata': {
                'username': 'teste',
                'full_name': 'Usuario Teste'
            }
        }
    ]

    print("Tentando criar usuarios via API...")

    for user in users:
        try:
            response = requests.post(auth_url, json=user, headers=headers)

            if response.status_code == 200:
                user_data = response.json()
                print(f"[OK] Usuario criado: {user['email']}")
                print(f"    ID: {user_data.get('id')}")

                # Criar profile
                create_profile_for_user(user_data['id'], user['user_metadata'])

            elif response.status_code == 422:
                print(f"[INFO] Usuario {user['email']} pode ja exister")
            else:
                print(f"[ERRO] Falha ao criar {user['email']}: {response.text}")

        except Exception as e:
            print(f"[ERRO] Exception ao criar {user['email']}: {e}")

def create_profile_for_user(user_id, metadata):
    """Cria profile para usuario criado"""
    config = load_config()

    headers = {
        'apikey': config['service_key'],
        'Authorization': f'Bearer {config["service_key"]}',
        'Content-Type': 'application/json',
        'Prefer': 'return=minimal'
    }

    profile_data = {
        'id': user_id,
        'username': metadata.get('username'),
        'full_name': metadata.get('full_name'),
        'role': 'admin' if metadata.get('username') == 'admin' else 'user'
    }

    rest_url = f"{config['url']}/rest/v1/profiles"

    try:
        response = requests.post(rest_url, json=profile_data, headers=headers)
        if response.status_code == 201:
            print(f"[OK] Profile criado para {metadata.get('username')}")
        else:
            print(f"[INFO] Profile {metadata.get('username')}: {response.text}")
    except Exception as e:
        print(f"[ERRO] Profile: {e}")

def main():
    """Funcao principal"""
    print("=== CRIACAO DE USUARIOS SUPABASE ===")
    print("Usando API REST do Supabase\n")

    # Verificar configuracao
    config = load_config()
    if not config['url'] or not config['service_key']:
        print("ERRO: Configure .env.supabase primeiro!")
        return False

    print(f"URL: {config['url']}")
    print(f"Service Key: Configurado\n")

    # Tentar criar usuarios
    create_users_via_api()

    # Verificar resultado
    print("\n=== VERIFICACAO ===")
    print("Verifique no dashboard:")
    print(f"Auth: {config['url'].replace('.co', '.co/auth/users')}")
    print(f"Profiles: {config['url'].replace('.co', '.co/project/jjxmfidggofuaxcdtkrd/editor')}")

    return True

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Erro: {e}")
        import traceback
        traceback.print_exc()