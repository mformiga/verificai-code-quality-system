import requests
import json

# URL da API
BASE_URL = "http://localhost:8000/api/v1/file-paths"

def cadastrar_arquivo(caminho_completo):
    """Cadastra um arquivo usando a API pública"""

    # Primeiro verifica se o arquivo já existe
    response = requests.get(f"{BASE_URL}/public")
    if response.status_code == 200:
        dados = response.json()
        for item in dados['items']:
            if item['full_path'] == caminho_completo:
                print(f"Arquivo já cadastrado: {caminho_completo}")
                return True

    # Cadastra o arquivo
    params = {"full_path": caminho_completo}
    response = requests.post(f"{BASE_URL}/public/create", params=params)

    if response.status_code == 200:
        resultado = response.json()
        print(f"Arquivo cadastrado com sucesso:")
        print(f"  ID: {resultado['id']}")
        print(f"  Caminho: {resultado['full_path']}")
        return True
    else:
        print(f"Erro ao cadastrar arquivo: {response.text}")
        return False

def listar_arquivos():
    """Lista todos os arquivos cadastrados"""
    response = requests.get(f"{BASE_URL}/public")
    if response.status_code == 200:
        dados = response.json()
        print(f"\nArquivos cadastrados ({dados['total']}):")
        print("=" * 50)
        for item in dados['items']:
            print(f"ID: {item['id']}")
            print(f"Arquivo: {item['file_name']}")
            print(f"Caminho: {item['full_path']}")
            print(f"Processado: {item['is_processed']}")
            print("-" * 30)
    else:
        print(f"Erro ao listar arquivos: {response.text}")

if __name__ == "__main__":
    print("Sistema de Cadastro de Arquivos para Análise")
    print("=" * 50)

    # Lista arquivos atuais
    listar_arquivos()

    print(f"\nCadastrar novo arquivo:")
    caminho = input("Digite o caminho completo do arquivo: ").strip()

    if caminho:
        if cadastrar_arquivo(caminho):
            print("\nArquivo cadastrado com sucesso!")
            listar_arquivos()
        else:
            print("\nFalha ao cadastrar arquivo.")