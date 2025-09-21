import json
import requests

# Testar análise com código fonte
url = "http://localhost:8000/api/v1/simple-analysis/simple-analyze"

data = {
    "criteria_ids": ["criteria_64", "criteria_66"],
    "file_paths": ["C:\\Users\\formi\\teste_gemini\\dev\\verificAI-code\\codigo_com_erros.ts"],
    "analysis_name": "Analise Completa com Codigo Fonte - Teste de Violacoes",
    "temperature": 0.7,
    "max_tokens": 4000
}

print("Testando analise com codigo fonte...")
print(f"Analisando {len(data['criteria_ids'])} criterios")

try:
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print("SUCESSO!")
        print(f"Nome: {result['analysis_name']}")
        print(f"Criterios analisados: {result['criteria_count']}")
        print(f"Modelo: {result['model_used']}")
        print(f"Tokens: {result['usage']['total_tokens']}")

        print("\n=== ANALISE DETALHADA ===")
        for key, criteria in result['criteria_results'].items():
            print(f"\nCriterio: {criteria['name'][:80]}...")
            print(f"Status: {criteria['content'][:30]}...")

        # Verificar se foram identificados erros
        if "Nao Conforme" in result['raw_response'] or "viol" in result['raw_response'].lower():
            print("\n*** VIOLACOES IDENTIFICADAS ***")
            print("O sistema identificou corretamente as violacoes no codigo!")

        print(f"\nResposta completa: {len(result['raw_response'])} caracteres")

    else:
        print(f"ERRO: {response.text}")

except Exception as e:
    print(f"ERRO na requisicao: {e}")