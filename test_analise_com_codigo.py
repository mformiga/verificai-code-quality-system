import json
import requests

# Testar análise com código fonte que contém violações
url = "http://localhost:8000/api/v1/simple-analysis/simple-analyze"

# Obter os critérios disponíveis
criteria_response = requests.get("http://localhost:8000/api/v1/simple-analysis/simple-results")
criteria_data = criteria_response.json()

print("=== CRITÉRIOS DISPONÍVEIS ===")
criterios = []
for result in criteria_data['results']:
    for key, criteria in result['criteria_results'].items():
        criterios.append(criteria['name'])
        print(f"- {criteria['name']}")

print(f"\nTotal de critérios únicos: {len(set(criterios))}")

# Testar com os dois critérios
data = {
    "criteria_ids": ["criteria_64", "criteria_66"],  # Ambos os critérios
    "file_paths": ["C:\\Users\\formi\\teste_gemini\\dev\\verificAI-code\\codigo_com_erros.ts"],
    "analysis_name": "Análise Completa com Código Fonte - Teste de Violações",
    "temperature": 0.7,
    "max_tokens": 4000
}

print("\n=== TESTANDO ANÁLISE COM CÓDIGO FONTE ===")
print(f"URL: {url}")
print(f"Analisando {len(data['criteria_ids'])} critérios")
print(f"Arquivo: {data['file_paths'][0]}")

try:
    response = requests.post(url, json=data)
    print(f"\nStatus Code: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print("\n=== RESULTADO DA ANÁLISE ===")
        print(f"✅ Sucesso: {result['success']}")
        print(f"📊 Nome: {result['analysis_name']}")
        print(f"🔢 Critérios analisados: {result['criteria_count']}")
        print(f"🤖 Modelo: {result['model_used']}")
        print(f"💰 Tokens: {result['usage']['total_tokens']}")

        print("\n=== ANÁLISE DETALHADA POR CRITÉRIO ===")
        for key, criteria in result['criteria_results'].items():
            print(f"\n📋 {key}: {criteria['name'][:50]}...")
            print(f"   Conteúdo: {criteria['content'][:200]}...")

        print(f"\n=== RESPOSTA COMPLETA ===")
        print(f"Tamanho da resposta: {len(result['raw_response'])} caracteres")
        print("\nPrimeiros 500 caracteres da resposta:")
        print(result['raw_response'][:500])

    else:
        print(f"❌ Erro: {response.text}")

except Exception as e:
    print(f"❌ Erro na requisição: {e}")