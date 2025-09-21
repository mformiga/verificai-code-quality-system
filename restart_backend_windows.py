#!/usr/bin/env python3
"""
Script para reiniciar o backend com as alterações mais recentes (Windows)
"""

import os
import sys
import subprocess
import time

def find_python_processes():
    """Encontra processos Python rodando o backend no Windows"""
    try:
        result = subprocess.run(['wmic', 'process', 'where', 'name="python.exe"', 'get', 'processid,commandline', '/format:list'],
                              capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
        lines = result.stdout.split('\n')
        python_processes = []
        current_pid = None

        for line in lines:
            line = line.strip()
            if line.startswith('CommandLine='):
                if 'app/main.py' in line or 'main:app' in line:
                    if current_pid:
                        python_processes.append(current_pid)
            elif line.startswith('ProcessId='):
                current_pid = line.split('=')[1]

        return python_processes
    except Exception as e:
        print(f"Erro ao encontrar processos: {e}")
        return []

def kill_process(pid):
    """Mata um processo pelo PID no Windows"""
    try:
        subprocess.run(['taskkill', '/PID', pid, '/F'],
                      capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        print(f"Processo {pid} morto com sucesso")
        return True
    except Exception as e:
        print(f"Erro ao matar processo {pid}: {e}")
        return False

def start_backend():
    """Inicia o backend"""
    try:
        # Mudar para o diretório backend
        backend_dir = r'C:\Users\formi\teste_gemini\dev\verificAI-code\backend'
        os.chdir(backend_dir)

        # Iniciar o backend
        env = os.environ.copy()
        env['PYTHONPATH'] = backend_dir

        # Iniciar em background sem esperar
        subprocess.Popen([
            sys.executable, '-m', 'uvicorn', 'main:app',
            '--host', '0.0.0.0', '--port', '3011', '--reload'
        ], env=env, creationflags=subprocess.CREATE_NEW_CONSOLE)

        print("Backend iniciado")
        return True
    except Exception as e:
        print(f"Erro ao iniciar backend: {e}")
        return False

if __name__ == "__main__":
    print("Reiniciando backend...")

    # Encontrar e matar processos existentes
    pids = find_python_processes()
    print(f"Processos encontrados: {pids}")

    for pid in pids:
        kill_process(pid)

    # Esperar um pouco
    time.sleep(3)

    # Iniciar novo backend
    success = start_backend()

    if success:
        print("Backend reiniciado com sucesso!")
        print("Aguarde alguns segundos para o backend iniciar completamente")
    else:
        print("Falha ao reiniciar backend")