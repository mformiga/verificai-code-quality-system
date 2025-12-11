import requests
import json

def test_backend_cors():
    """Testar CORS no backend do Vercel"""

    backend_url = "https://verificai-backend-1mmrfd0n7-mauricios-projects-b3859180.vercel.app"

    # Testar endpoint raiz primeiro
    print("Testando endpoint raiz...")
    try:
        response = requests.get(f"{backend_url}/")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Erro: {e}")

    # Testar OPTIONS para login
    print("\nTestando OPTIONS para /api/v1/login/json...")

    headers = {
        "Origin": "https://verificai-frontend.vercel.app",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "Content-Type, Authorization"
    }

    try:
        response = requests.options(f"{backend_url}/api/v1/login/json", headers=headers)
        print(f"Status: {response.status_code}")
        print("Headers de resposta:")
        for k, v in response.headers.items():
            print(f"  {k}: {v}")

        # Verificar CORS headers especificamente
        cors_headers = {k: v for k, v in response.headers.items() if 'access-control' in k.lower()}
        print(f"\nCORS Headers: {cors_headers}")

    except Exception as e:
        print(f"Erro: {e}")

    # Testar POST real
    print("\nTestando POST real...")
    headers = {
        "Origin": "https://verificai-frontend.vercel.app",
        "Content-Type": "application/json"
    }

    data = {
        "username": "test@example.com",
        "password": "test123"
    }

    try:
        response = requests.post(f"{backend_url}/api/v1/login/json",
                               json=data,
                               headers=headers)
        print(f"Status: {response.status_code}")
        print("Headers de resposta:")
        for k, v in response.headers.items():
            if 'access-control' in k.lower():
                print(f"  {k}: {v}")
        if response.text:
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    test_backend_cors()