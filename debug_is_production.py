#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para debugar a função is_production()
"""

import os
import sys
from dotenv import load_dotenv

# Configurar encoding para Windows
if sys.platform == 'win32':
    os.system('chcp 65001 > nul')

print("=" * 60)
print("DEBUG DA FUNÇÃO is_production()")
print("=" * 60)

# Simular a lógica da função
print("1. Carregando arquivos .env na ordem...")

# Carregar na ordem que a função faz
if os.path.exists('.env.local_supabase'):
    print("   Carregando .env.local_supabase")
    load_dotenv('.env.local_supabase')
if os.path.exists('.env.local'):
    print("   Carregando .env.local")
    load_dotenv('.env.local')
if os.path.exists('.env'):
    print("   Carregando .env")
    load_dotenv('.env')

# Verificar variáveis de ambiente primeiro
env_production = (
    os.getenv('ENVIRONMENT') == 'production' or
    os.getenv('IS_STREAMLIT_CLOUD') == 'true' or
    os.getenv('FORCE_PRODUCTION') == 'true'
)

# Verificar se está no Streamlit Cloud
streamlit_cloud = 'STREAMLIT_SHARING' in os.environ

# Verificar se tem arquivo local de configuração
has_local_env = os.path.exists('.env.local')
has_local_supabase = os.path.exists('.env.local_supabase')

# Lógica corrigida
is_prod = env_production or streamlit_cloud

print(f"\n2. Variáveis de ambiente:")
print(f"   ENVIRONMENT: '{os.getenv('ENVIRONMENT', 'not_set')}'")
print(f"   IS_STREAMLIT_CLOUD: '{os.getenv('IS_STREAMLIT_CLOUD', 'not_set')}'")
print(f"   FORCE_PRODUCTION: '{os.getenv('FORCE_PRODUCTION', 'not_set')}'")
print(f"   STREAMLIT_SHARING: {'present' if streamlit_cloud else 'absent'}")

print(f"\n3. Arquivos locais:")
print(f"   .env.local: {'exists' if has_local_env else 'absent'}")
print(f"   .env.local_supabase: {'exists' if has_local_supabase else 'absent'}")

print(f"\n4. Cálculos:")
print(f"   env_production: {env_production}")
print(f"   streamlit_cloud: {streamlit_cloud}")
print(f"   is_prod (resultado final): {is_prod}")

print(f"\n5. RESULTADO:")
print(f"   is_production() retornaria: {'PRODUÇÃO' if is_prod else 'DESENVOLVIMENTO'}")

print(f"\n6. Verificação de variáveis que podem estar causando problema:")
all_env_vars = [k for k in os.environ.keys() if 'ENV' in k or 'PROD' in k or 'STREAMLIT' in k]
for var in all_env_vars:
    print(f"   {var}: '{os.environ[var]}'")

print(f"\n7. Variáveis de interesse específico:")
interesting_vars = ['ENVIRONMENT', 'IS_STREAMLIT_CLOUD', 'FORCE_PRODUCTION', 'STREAMLIT_SHARING']
for var in interesting_vars:
    value = os.environ.get(var, 'NOT_SET')
    print(f"   {var}: '{value}'")