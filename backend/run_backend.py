#!/usr/bin/env python3
"""
Script para executar o backend corretamente
"""

import os
import sys
import subprocess

def main():
    # Mudar para diretório backend
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(backend_dir)

    # Configurar PYTHONPATH
    env = os.environ.copy()
    env['PYTHONPATH'] = backend_dir

    print(f"Diretório: {backend_dir}")
    print(f"PYTHONPATH: {env['PYTHONPATH']}")

    # Executar uvicorn
    subprocess.run([
        sys.executable, '-m', 'uvicorn', 'app.main:app',
        '--host', '0.0.0.0',
        '--port', '3011',
        '--reload'
    ], env=env)

if __name__ == '__main__':
    main()