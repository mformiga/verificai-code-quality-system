#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Atualizar profiles dos usuarios criados
"""

import os
import requests
from pathlib import Path

def load_config():
    """Carrega configuracao"""
    env_file = Path(".env.supabase")
    if env_file.exists():
        from dotenv import load_dotenv
        load_dotenv(env_file)

    return {
        'url': os.getenv('SUPABASE_URL'),
        'service_key': os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    }

def update_user_profiles():
    """Atualiza profiles com metadados corretos"""
    config = load_config()

    headers = {
        'apikey': config['service_key'],
        'Authorization': f'Bearer {config["service_key"]}',
        'Content-Type': 'application/json',
        'Prefer': 'return=minimal'
    }

    rest_url = f"{config['url']}/rest/v1/profiles"

    # Usuarios criados com seus IDs
    users = [
        {
            'id': '7e247de9-ccd1-4065-a5ad-db5f5e411811',
            'username': 'admin',
            'full_name': 'Administrator',
            'role': 'admin'
        },
        {
            'id': 'b282b73e-ecfe-4753-8df9-c4621635460d',
            'username': 'teste',
            'full_name': 'Usuario Teste',
            'role': 'user'
        }
    ]

    print("Atualizando profiles...")

    for user in users:
        try:
            # Usar PATCH para atualizar
            response = requests.patch(
                f"{rest_url}?id=eq.{user['id']}",
                json={
                    'username': user['username'],
                    'full_name': user['full_name'],
                    'role': user['role'],
                    'updated_at': '2025-12-05T21:00:00Z'
                },
                headers=headers
            )

            if response.status_code == 204:
                print(f"[OK] Profile atualizado: {user['username']}")
            elif response.status_code == 200:
                print(f"[OK] Profile atualizado: {user['username']}")
            else:
                print(f"[INFO] Profile {user['username']}: {response.status_code}")

        except Exception as e:
            print(f"[ERRO] {user['username']}: {e}")

def verify_profiles():
    """Verifica se profiles foram atualizados"""
    config = load_config()

    headers = {
        'apikey': config['service_key'],
        'Authorization': f'Bearer {config["service_key"]}'
    }

    rest_url = f"{config['url']}/rest/v1/profiles?select=id,username,full_name,role&order=username"

    try:
        response = requests.get(rest_url, headers=headers)
        if response.status_code == 200:
            profiles = response.json()
            print("\nProfiles atuais:")
            for profile in profiles:
                print(f"  - {profile['username']} ({profile['role']}) - {profile['full_name']}")
        else:
            print(f"Erro ao verificar: {response.status_code}")

    except Exception as e:
        print(f"Erro: {e}")

def main():
    """Funcao principal"""
    print("=== ATUALIZACAO DE PROFILES ===")

    update_user_profiles()
    verify_profiles()

    print("\n=== LOGIN TESTE ===")
    print("Tente fazer login com:")
    print("Email: admin@avalia.com")
    print("Senha: admin123")
    print("\nOU")
    print("Email: teste@avalia.com")
    print("Senha: teste123")
    print("\nApp: http://localhost:8501")

if __name__ == "__main__":
    main()