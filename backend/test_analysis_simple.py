#!/usr/bin/env python3
"""
Script simples para testar comportamento do sistema quando não há arquivos no banco de dados
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
import json

def test_analysis_without_files():
    """Testa o comportamento do sistema quando não há arquivos no banco de dados"""

    base_url = "http://localhost:8000"

    print("TESTE: Analise sem arquivos no banco de dados")
    print("=" * 60)

    # 1. Testar sem autenticação
    print("\n1. Testando API sem autenticacao...")

    try:
        response = requests.get(f"{base_url}/api/v1/file-paths/")
        print(f"   Status file-paths: {response.status_code}")

        if response.status_code == 401 or response.status_code == 403:
            print("   OK API protegida por autenticacao")
        else:
            print(f"   WARNING Resposta inesperada: {response.text[:100]}")

    except Exception as e:
        print(f"   ERRO ao conectar: {e}")

    # 2. Tentar fazer login
    print("\n2. Tentando login...")

    try:
        login_data = {
            "username": "admin",
            "password": "admin123"
        }

        response = requests.post(f"{base_url}/api/v1/auth/login", data=login_data)

        if response.status_code == 200:
            auth_data = response.json()
            token = auth_data.get("access_token")
            print("   OK Login realizado com sucesso")

            headers = {"Authorization": f"Bearer {token}"}

            # 3. Verificar file paths
            print("\n3. Verificando file paths...")

            response = requests.get(f"{base_url}/api/v1/file-paths/", headers=headers)

            if response.status_code == 200:
                paths_data = response.json()
                file_count = len(paths_data.get("file_paths", []))
                print(f"   INFO Arquivos no banco: {file_count}")

                if file_count == 0:
                    print("   OK Banco de dados esta vazio")
                else:
                    print("   WARNING Banco ainda contem arquivos")
            else:
                print(f"   ERRO ao consultar file paths: {response.status_code}")

            # 4. Testar análise sem arquivos
            print("\n4. Testando analise sem arquivos...")

            analysis_request = {
                "criteria_ids": ["1", "2"],
                "file_paths": []
            }

            response = requests.post(
                f"{base_url}/api/v1/general-analysis/analyze-selected",
                json=analysis_request,
                headers=headers
            )

            print(f"   Status analise sem arquivos: {response.status_code}")

            if response.status_code != 200:
                error_data = response.text
                print(f"   DETALHE Erro: {error_data[:200]}")

                if "No file paths provided" in error_data:
                    print("   OK Sistema validou ausencia de arquivos (inglês)")
                elif "Nenhum arquivo" in error_data:
                    print("   OK Sistema validou ausencia de arquivos (português)")
                else:
                    print("   WARNING Resposta de erro nao esperada")
            else:
                print("   ERRO Analise deveria falhar sem arquivos!")
                result = response.json()
                print(f"   RESULTADO: {result}")

            # 5. Testar com caminhos inválidos
            print("\n5. Testando analise com caminhos invalidos...")

            invalid_request = {
                "criteria_ids": ["1", "2"],
                "file_paths": ["/caminho/inexistente/arquivo.tsx"]
            }

            response = requests.post(
                f"{base_url}/api/v1/general-analysis/analyze-selected",
                json=invalid_request,
                headers=headers
            )

            print(f"   Status analise com paths invalidos: {response.status_code}")

            if response.status_code != 200:
                error_data = response.text
                print(f"   DETALHE Erro: {error_data[:200]}")

                if "Nenhum arquivo" in error_data or "nao pode ser lido" in error_data:
                    print("   OK Sistema detectou arquivos ilegiveis")
            else:
                print("   ERRO Analise deveria falhar com paths invalidos!")

        else:
            print(f"   ERRO Falha no login: {response.status_code}")
            print(f"   DETALHE: {response.text[:200]}")

    except Exception as e:
        print(f"   ERRO durante teste: {e}")

    print("\n" + "=" * 60)
    print("TESTE CONCLUIDO")
    print("=" * 60)

if __name__ == "__main__":
    test_analysis_without_files()