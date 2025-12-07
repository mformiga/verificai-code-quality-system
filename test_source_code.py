#!/usr/bin/env python3
"""
Test script para verificar se o endpoint source-code funciona
"""

import requests
import json

def test_source_code_endpoint():
    """Testa o endpoint POST /api/v1/source-code/"""

    url = "http://localhost:8000/api/v1/source-code/"

    data = {
        "title": "Teste de Código",
        "description": "Código de teste via script Python",
        "content": "def hello_world():\n    print(\"Hello, World!\")\n    return \"Hello, World!\"",
        "file_name": "hello.py",
        "file_extension": ".py",
        "programming_language": "Python",
        "category": "function",
        "tags": ["test", "hello", "script"],
        "is_public": False,
        "is_template": False
    }

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    try:
        print(f"🔄 Fazendo POST para {url}")
        print(f"📤 Data: {json.dumps(data, indent=2)}")

        response = requests.post(url, json=data, headers=headers, timeout=30)

        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Headers: {dict(response.headers)}")

        if response.status_code == 200:
            print("✅ Sucesso!")
            result = response.json()
            print(f"📄 Response: {json.dumps(result, indent=2)}")

            # Verificar se salvou no banco
            if result.get('id'):
                print(f"💾 Código salvo com ID: {result['id']}")
                print(f"📁 Título: {result['title']}")
                print(f"🐍 Linguagem: {result.get('programming_language', 'N/A')}")
                print(f"📏 Linhas: {result.get('line_count', 'N/A')}")
                print(f"💾 Tamanho: {result.get('size_bytes', 'N/A')} bytes")
                return True
        else:
            print("❌ Erro!")
            try:
                error_data = response.json()
                print(f"📄 Error Response: {json.dumps(error_data, indent=2)}")
            except:
                print(f"📄 Error Text: {response.text}")

        return False

    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def test_root_endpoint():
    """Testa o endpoint raiz para verificar conectividade"""
    try:
        response = requests.get("http://localhost:8000/")
        if response.status_code == 200:
            print("✅ Conexão com backend está funcionando")
            return True
        else:
            print(f"❌ Erro no endpoint raiz: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao conectar no backend: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testando endpoint source-code...")

    if test_root_endpoint():
        success = test_source_code_endpoint()

        if success:
            print("\n🎉 Teste concluído com sucesso! O endpoint está funcionando.")
            print("💡 O código foi salvo na tabela source_codes do PostgreSQL local.")
        else:
            print("\n💥 Teste falhou! Verifique os logs do backend.")
    else:
        print("\n💥 Não foi possível conectar ao backend. Verifique se está rodando em http://localhost:8000")