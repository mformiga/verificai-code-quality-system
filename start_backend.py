#!/usr/bin/env python3
"""
Script para iniciar o backend corretamente
"""

import os
import sys
import subprocess
import time

def start_backend():
    """Inicia o backend na porta 3011"""
    backend_dir = r'C:\Users\formi\teste_gemini\dev\verificAI-code\backend'

    print(f"Iniciando backend na porta 3011...")
    print(f"Diretório: {backend_dir}")

    try:
        # Mudar para diretório do backend
        os.chdir(backend_dir)

        # Configurar ambiente
        env = os.environ.copy()
        env['PYTHONPATH'] = backend_dir

        # Iniciar backend sem modo de recarregamento para evitar problemas
        process = subprocess.Popen([
            sys.executable, '-m', 'uvicorn', 'main:app',
            '--host', '0.0.0.0', '--port', '3011'
        ], env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        print(f"Backend iniciado com PID {process.pid}")
        print("Aguardando inicialização...")

        # Esperar um pouco para inicializar
        time.sleep(3)

        return process

    except Exception as e:
        print(f"Erro ao iniciar backend: {e}")
        return None

def test_backend():
    """Testa se o backend está respondendo"""
    import requests

    try:
        response = requests.get('http://localhost:3011/health', timeout=5)
        if response.status_code == 200:
            print("✓ Backend está respondendo!")
            return True
        else:
            print(f"✗ Backend retornou status {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Erro ao testar backend: {e}")
        return False

if __name__ == "__main__":
    # Iniciar backend
    backend_process = start_backend()

    if backend_process:
        # Testar backend
        if test_backend():
            print("\n✓ Backend iniciado com sucesso!")
            print("Agora você pode acessar http://localhost:3011")
        else:
            print("\n✗ Backend não está respondendo corretamente")
            print("Verifique os logs acima para mais detalhes")

        # Manter script rodando
        print("\nPressione Ctrl+C para parar o backend...")
        try:
            backend_process.wait()
        except KeyboardInterrupt:
            print("\nParando backend...")
            backend_process.terminate()
    else:
        print("✗ Falha ao iniciar backend")