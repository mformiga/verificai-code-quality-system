#!/usr/bin/env python3
"""
Script para testar configuração CORS entre frontend e backend
"""

import requests
import json

def test_cors():
    """Testar se CORS está configurado corretamente"""

    # Backend URL
    backend_url = "https://verificai-backend-1mmrfd0n7-mauricios-projects-b3859180.vercel.app"

    # Testar OPTIONS request para login endpoint
    login_endpoint = f"{backend_url}/api/v1/login/json"

    headers = {
        "Origin": "https://verificai-frontend.vercel.app",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "Content-Type, Authorization"
    }

    print("🔍 Testando configuração CORS...")
    print(f"Backend URL: {backend_url}")
    print(f"Origin: {headers['Origin']}")
    print(f"Endpoint: {login_endpoint}")

    try:
        # Testar preflight request
        print("\n📤 Enviando OPTIONS request (preflight)...")
        response = requests.options(login_endpoint, headers=headers)

        print(f"Status Code: {response.status_code}")
        print("CORS Headers:")
        for header, value in response.headers.items():
            if 'access-control' in header.lower():
                print(f"  {header}: {value}")

        # Verificar se origin está permitida
        if 'Access-Control-Allow-Origin' in response.headers:
            allowed_origin = response.headers['Access-Control-Allow-Origin']
            if allowed_origin == headers['Origin'] or allowed_origin == '*':
                print("✅ Origin permitida!")
            else:
                print(f"⚠️ Origin não corresponde: {allowed_origin}")
        else:
            print("❌ Access-Control-Allow-Origin não encontrado!")

        # Testar request real
        print("\n📤 Testando POST request real...")
        test_data = {
            "username": "test@example.com",
            "password": "testpassword"
        }

        post_headers = {
            "Origin": "https://verificai-frontend.vercel.app",
            "Content-Type": "application/json"
        }

        response = requests.post(login_endpoint,
                               data=json.dumps(test_data),
                               headers=post_headers)

        print(f"Status Code: {response.status_code}")
        print("CORS Headers na resposta:")
        for header, value in response.headers.items():
            if 'access-control' in header.lower():
                print(f"  {header}: {value}")

        return True

    except requests.exceptions.RequestException as e:
        print(f"❌ Erro na requisição: {e}")
        return False

if __name__ == "__main__":
    test_cors()