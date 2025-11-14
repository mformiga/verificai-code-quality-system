#!/usr/bin/env python3
"""
Script para reiniciar o backend com as alterações mais recentes
"""

import os
import sys
import subprocess
import signal
import time

def find_python_processes():
    """Encontra processos Python rodando o backend"""
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        python_processes = []
        for line in lines:
            if 'python' in line and 'app/main.py' in line:
                parts = line.split()
                if len(parts) > 1:
                    pid = parts[1]
                    python_processes.append(pid)
        return python_processes
    except Exception as e:
        print(f"Erro ao encontrar processos: {e}")
        return []

def kill_process(pid):
    """Mata um processo pelo PID"""
    try:
        os.kill(int(pid), signal.SIGTERM)
        print(f"Processo {pid} morto com sucesso")
        return True
    except Exception as e:
        print(f"Erro ao matar processo {pid}: {e}")
        return False

def start_backend():
    """Inicia o backend"""
    try:
        # Mudar para o diretório backend
        os.chdir('/c/Users/formi/teste_gemini/dev/verificAI-code/backend')

        # Iniciar o backend
        env = os.environ.copy()
        env['PYTHONPATH'] = '.'

        process = subprocess.Popen([
            sys.executable, 'app/main.py'
        ], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        print(f"Backend iniciado com PID {process.pid}")
        return process
    except Exception as e:
        print(f"Erro ao iniciar backend: {e}")
        return None

if __name__ == "__main__":
    print("Reiniciando backend...")

    # Encontrar e matar processos existentes
    pids = find_python_processes()
    for pid in pids:
        kill_process(pid)

    # Esperar um pouco
    time.sleep(2)

    # Iniciar novo backend
    backend_process = start_backend()

    if backend_process:
        print("Backend reiniciado com sucesso!")
    else:
        print("Falha ao reiniciar backend")