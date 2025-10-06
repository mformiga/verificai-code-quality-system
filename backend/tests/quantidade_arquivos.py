import os

caminho = r"C:\Users\formi\teste_gemini\dev\verificAI-code\backend\tests\sistema_teste"  # coloque aqui o caminho da pasta que quer contar
contador = sum(len(files) for _, _, files in os.walk(caminho))

print(f"Total de arquivos: {contador}")