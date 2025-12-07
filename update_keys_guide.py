#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Guia para obter e atualizar chaves do Supabase
"""

import os
import webbrowser

def main():
    print("=== CONFIGURAR CHAVES SUPABASE ===")
    print()
    print("🔑 Você precisa configurar suas chaves reais!")
    print()
    print("📋 PASSOS:")
    print()
    print("1. Abra seu projeto Supabase:")
    print("   URL: https://app.supabase.com/project/jjxmfidggofuaxcdtkrd/settings/api")
    print()
    print("2. Copie as chaves:")
    print("   - Project URL (já correto)")
    print("   - anon public key")
    print("   - service_role key")
    print()
    print("3. Atualize o arquivo .env.supabase:")
    print()
    print("   SUPABASE_URL=https://jjxmfidggofuaxcdtkrd.supabase.co")
    print("   SUPABASE_ANON_KEY=SUA_CHAVE_ANON_REAL")
    print("   SUPABASE_SERVICE_ROLE_KEY=SUA_CHAVE_SERVICE_REAL")
    print("   SUPABASE_PROJECT_REF=jjxmfidggofuaxcdtkrd")
    print()
    print("4. Salve o arquivo e reinicie o Streamlit:")
    print("   streamlit run app.py")
    print()
    print("🌐 Abrindo seu dashboard Supabase...")

    # Tenta abrir o navegador
    try:
        webbrowser.open("https://app.supabase.com/project/jjxmfidggofuaxcdtkrd/settings/api")
        print("✅ Dashboard aberto no navegador")
    except:
        print("❌ Não foi possível abrir o navegador automaticamente")
        print("   Abra manualmente: https://app.supabase.com/project/jjxmfidggofuaxcdtkrd/settings/api")

if __name__ == "__main__":
    main()