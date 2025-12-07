#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from pathlib import Path

def check_supabase_setup():
    """Verifica configuracao do Supabase"""

    print("=== VERIFICACAO SUPABASE ===")
    print(f"Project Ref: jjxmfidggofuaxcdtkrd")

    # Verificar arquivo de ambiente
    env_file = Path(".env.supabase")
    if env_file.exists():
        print("[OK] Arquivo .env.supabase encontrado")

        # Carregar variaveis
        with open(env_file, 'r') as f:
            content = f.read()

        if "jjxmfidggofuaxcdtkrd" in content:
            print("[OK] Project ref configurado")
        else:
            print("[ERRO] Project ref nao configurado")

        # Verificar variaveis
        required_vars = ["SUPABASE_URL", "SUPABASE_ANON_KEY", "SUPABASE_PROJECT_REF"]
        for var in required_vars:
            if f"{var}=" in content:
                print(f"[OK] {var} encontrado")
            else:
                print(f"[ERRO] {var} nao encontrado")
    else:
        print("[ERRO] Arquivo .env.supabase nao encontrado")

    # Verificar arquivos SQL
    sql_files = [
        "supabase_schema_fixed.sql",
        "supabase_storage_setup.sql"
    ]

    for sql_file in sql_files:
        if Path(sql_file).exists():
            print(f"[OK] {sql_file} encontrado")
        else:
            print(f"[ERRO] {sql_file} nao encontrado")

    # Verificar app.py
    if Path("app.py").exists():
        print("[OK] app.py encontrado")

        with open("app.py", 'r') as f:
            app_content = f.read()

        if "supabase_client" in app_content:
            print("[OK] app.py usa supabase_client")
        else:
            print("[AVISO] app.py pode nao estar configurado para Supabase")

        if "render.com" in app_content.lower():
            print("[AVISO] Ainda ha referencias ao Render")
        else:
            print("[OK] Sem referencias ao Render")
    else:
        print("[ERRO] app.py nao encontrado")

    print("\n=== INSTRUCOES ===")
    print("1. Obtenha suas chaves em: https://app.supabase.com/project/jjxmfidggofuaxcdtkrd/settings/api")
    print("2. Atualize .env.supabase com suas chaves")
    print("3. Execute o schema SQL no Supabase SQL Editor")
    print("4. Execute: pip install -r requirements.txt")
    print("5. Execute: streamlit run app.py")

    print("\n=== URLS UTEIS ===")
    print("Supabase Dashboard: https://app.supabase.com/project/jjxmfidggofuaxcdtkrd")
    print("Supabase SQL Editor: https://app.supabase.com/project/jjxmfidggofuaxcdtkrd/sql/new")
    print("Supabase Settings: https://app.supabase.com/project/jjxmfidggofuaxcdtkrd/settings")

if __name__ == "__main__":
    check_supabase_setup()