#!/usr/bin/env python3
"""
Test script for PUT endpoint
"""

import requests
import json

# Test data
test_data = {
    "criterion_key": "criteria_66",
    "criterion_data": {
        "name": "Teste Update",
        "content": "Conteúdo atualizado via script Python"
    }
}

# Test the debug endpoint (no auth required)
url = "http://localhost:8001/api/v1/general-analysis/debug-test-put/196"

try:
    print(f"Testing PUT to: {url}")
    print(f"Data: {json.dumps(test_data, indent=2)}")

    response = requests.put(
        url,
        json=test_data,
        headers={"Content-Type": "application/json"},
        timeout=10
    )

    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"Response Body: {response.text}")

    if response.status_code == 200:
        print("✅ SUCCESS: PUT endpoint is working!")
    else:
        print("❌ FAILED: PUT endpoint returned error")

except requests.exceptions.RequestException as e:
    print(f"❌ ERROR: Request failed: {e}")
except Exception as e:
    print(f"❌ ERROR: {e}")

# Test with real result data
print("\n" + "="*50)
print("Testing with actual result data structure...")

real_data = {
    "criterion_key": "criteria_66",
    "criterion_data": {
        "name": "Princípios SOLID: Analisar violações do Princípio da Responsabilidade Única (SRP), como controllers com múltiplos endpoints, e do Princípio da Inversão de Dependência (DI), como a instanciação manual de dependências em vez de usar a injeção padrão do NestJS.",
        "content": "## Avaliação Atualizada\n\nEsta é uma versão atualizada da avaliação que foi modificada manualmente via API.\n\n**Status:** Parcialmente Conforme\n**Confiança:** 0.8\n\n### Evidências:\n- O código apresenta múltiplas responsabilidades\n- Há instanciação manual de dependências\n- Violação do princípio SRP\n\n### Recomendações:\n1. Implementar injeção de dependências\n2. Separar responsabilidades\n3. Usar decorators do NestJS"
    }
}

try:
    response = requests.put(
        url,
        json=real_data,
        headers={"Content-Type": "application/json"},
        timeout=10
    )

    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")

    if response.status_code == 200:
        print("✅ SUCCESS: Real data test passed!")
        result = response.json()
        if result.get("success"):
            print("✅ Database update successful!")
    else:
        print("❌ FAILED: Real data test failed")

except Exception as e:
    print(f"❌ ERROR: {e}")