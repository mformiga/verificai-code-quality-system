import json
import requests

# Verificar resultados salvos no banco
url = "http://localhost:8000/api/v1/simple-analysis/simple-results"

try:
    response = requests.get(url)
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print("RESULTADOS SALVOS NO BANCO:")
        print(f"Total de análises: {result.get('total', 0)}")

        if result.get('results'):
            for i, analysis in enumerate(result['results']):
                print(f"\n=== ANÁLISE {i+1} ===")
                print(f"ID: {analysis['id']}")
                print(f"Nome: {analysis['analysis_name']}")
                print(f"Critérios: {analysis['criteria_count']}")
                print(f"Timestamp: {analysis['timestamp']}")
                print(f"Modelo: {analysis['model_used']}")

                # Mostrar critérios analisados
                if analysis['criteria_results']:
                    print("Critérios analisados:")
                    for key, criteria in analysis['criteria_results'].items():
                        print(f"  - {criteria['name']}")

                print("-" * 50)
        else:
            print("NENHUM RESULTADO ENCONTRADO NO BANCO!")
            print("Isso indica que as análises não estão sendo persistidas.")
    else:
        print(f"ERRO: {response.text}")

except Exception as e:
    print(f"ERRO NA REQUISIÇÃO: {e}")