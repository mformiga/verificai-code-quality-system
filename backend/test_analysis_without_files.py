#!/usr/bin/env python3
"""
Script para testar comportamento do sistema quando não há arquivos no banco de dados
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import asyncio
import aiohttp
import json
from datetime import datetime

async def test_analysis_without_files():
    """Testa o comportamento do sistema quando não há arquivos no banco de dados"""

    # URL base da API
    base_url = "http://localhost:8000"

    print("TESTE: Analise sem arquivos no banco de dados")
    print("=" * 60)

    # 1. Verificar status do banco de dados
    print("\n1. Verificando status do banco de dados...")

    try:
        async with aiohttp.ClientSession() as session:
            # Verificar file paths (sem autenticação primeiro)
            async with session.get(f"{base_url}/api/v1/file-paths/") as response:
                print(f"   Status API file-paths: {response.status}")
                if response.status == 403:
                    print("   API corretamente protegida por autenticação")
                else:
                    print(f"   WARNING Resposta inesperada: {await response.text()}")

            print("\n2. Testando endpoint de análise sem autenticação...")

            # Testar análise sem autenticação
            analysis_request = {
                "criteria_ids": ["1", "2"],
                "file_paths": []
            }

            async with session.post(
                f"{base_url}/api/v1/general-analysis/analyze-selected",
                json=analysis_request
            ) as response:
                print(f"   Status análise sem auth: {response.status}")
            if response.status == 403:
                    print("   Analise corretamente bloqueada sem autenticacao")
                else:
                    print(f"   WARNING Resposta inesperada: {await response.text()}")

        print("\n3. Testando login para obter token...")

            # Tentar fazer login
            login_data = {
                "username": "admin",
                "password": "admin123"
            }

            async with session.post(
                f"{base_url}/api/v1/auth/login",
                data=login_data
            ) as response:
            if response.status == 200:
                auth_data = await response.json()
                token = auth_data.get("access_token")
                print("   Login realizado com sucesso")

                # Testar com autenticação
                headers = {"Authorization": f"Bearer {token}"}

                print("\n4. Verificando file paths com autenticacao...")

                async with session.get(
                    f"{base_url}/api/v1/file-paths/",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        paths_data = await response.json()
                        file_count = len(paths_data.get("file_paths", []))
                        print(f"   INFO Arquivos no banco: {file_count}")

                        if file_count == 0:
                            print("   OK Banco de dados está vazio (como esperado)")
                        else:
                            print("   WARNING Banco ainda contém arquivos")
                    else:
                        print(f"   ERRO Erro ao consultar file paths: {response.status}")

                print("\n5. Testando analise sem arquivos...")

                # Tentar fazer análise mesmo sem arquivos
                async with session.post(
                    f"{base_url}/api/v1/general-analysis/analyze-selected",
                    json=analysis_request,
                    headers=headers
                ) as response:
                    print(f"   Status análise sem arquivos: {response.status}")

                    if response.status != 200:
                        error_data = await response.text()
                        print(f"   DETALHE Erro retornado: {error_data}")

                        if "No file paths provided" in error_data:
                            print("   OK Sistema corretamente validou ausência de arquivos")
                        elif "Nenhum arquivo" in error_data:
                            print("   OK Sistema retornou mensagem em português")
                        else:
                            print("   WARNING Resposta de erro não esperada")
                    else:
                        print("   ERRO Análise deveria falhar sem arquivos!")
                        result = await response.json()
                        print(f"   RESULTADO Resultado inesperado: {result}")

                print("\n6. Testando analise com file paths invalidos...")

                # Testar com file paths que não existem
                invalid_analysis_request = {
                    "criteria_ids": ["1", "2"],
                    "file_paths": ["/caminho/inexistente/arquivo.tsx"]
                }

                async with session.post(
                    f"{base_url}/api/v1/general-analysis/analyze-selected",
                    json=invalid_analysis_request,
                    headers=headers
                ) as response:
                    print(f"   Status análise com paths inválidos: {response.status}")

                    if response.status != 200:
                        error_data = await response.text()
                        print(f"   DETALHE Erro: {error_data}")

                        if "Nenhum arquivo pôde ser lido" in error_data:
                            print("   OK Sistema corretamente detectou arquivos ilegíveis")
                    else:
                        print("   ERRO Análise deveria falhar com paths inválidos!")

            else:
                print(f"   ERRO Falha no login: {response.status}")
                print(f"   DETALHE Resposta: {await response.text()}")

    except aiohttp.ClientError as e:
        print(f"ERRO Erro de conexão com a API: {e}")
        print("   Verifique se o backend está rodando em localhost:8000")

    except Exception as e:
        print(f"ERRO Erro inesperado: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 60)
    print("TESTE CONCLUIDO")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_analysis_without_files())