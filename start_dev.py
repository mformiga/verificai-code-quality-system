#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para iniciar a aplicação em modo desenvolvimento forçado
"""

import os
import sys
import subprocess

# Forçar ambiente de desenvolvimento
os.environ['ENVIRONMENT'] = 'development'
os.environ['FORCE_PRODUCTION'] = 'false'

print("=== INICIANDO APLICAÇÃO EM MODO DESENVOLVIMENTO ===")
print(f"ENVIRONMENT: {os.environ.get('ENVIRONMENT')}")
print(f"FORCE_PRODUCTION: {os.environ.get('FORCE_PRODUCTION')}")
print()

# Iniciar a aplicação Streamlit
cmd = ['streamlit', 'run', 'app.py', '--server.port', '8517']
subprocess.run(cmd, cwd=os.getcwd())