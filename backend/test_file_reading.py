import os

def test_file_reading():
    # Testar o caminho que o frontend está enviando
    test_paths = [
        r'C:\Users\formi\teste_gemini\dev\verificAI-code\codigo_para_analise\codigo_analise.ts',
        r'C:\\Users\\formi\\teste_gemini\\dev\\verificAI-code\\codigo_para_analise\\codigo_analise.ts',
        'C:\\Users\\formi\\teste_gemini\\dev\\verificAI-code\\codigo_para_analise\\codigo_analise.ts'
    ]

    for path in test_paths:
        print(f"\nTestando caminho: {path}")
        try:
            if os.path.exists(path):
                print("[OK] Arquivo existe")

                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')

                print("[OK] Arquivo lido com sucesso")
                print(f"   - Tamanho: {len(content)} caracteres")
                print(f"   - Linhas: {len(lines)}")
                print(f"   - Preview: {content[:100]}...")
            else:
                print("[ERRO] Arquivo não encontrado")
        except Exception as e:
            print(f"[ERRO] Erro ao ler arquivo: {e}")

if __name__ == "__main__":
    test_file_reading()