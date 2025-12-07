#!/usr/bin/env python3
"""
Test Setup Local - AVALIA
Verifica configuração local sem precisar de MCP
"""

import os
import sys
from pathlib import Path

def check_files():
    """Verifica se todos os arquivos necessários existem"""
    print("🔍 Verificando arquivos de configuração...")

    required_files = [
        "app.py",
        "requirements.txt",
        ".streamlit/config.toml",
        "supabase_schema_fixed.sql",
        "supabase_storage_setup.sql",
        "backend/app/core/supabase.py",
        "get_supabase_info.py",
        "validate_supabase_setup.py"
    ]

    missing_files = []

    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            missing_files.append(file_path)

    return len(missing_files) == 0, missing_files

def check_requirements():
    """Verifica requirements.txt"""
    print("\n📦 Verificando requirements.txt...")

    req_file = Path("requirements.txt")
    if not req_file.exists():
        print("❌ requirements.txt não encontrado")
        return False

    with open(req_file, 'r') as f:
        requirements = f.read()

    required_packages = [
        "streamlit",
        "supabase",
        "requests",
        "pandas",
        "python-dotenv"
    ]

    missing_packages = []
    for package in required_packages:
        if package in requirements.lower():
            print(f"✅ {package}")
        else:
            print(f"❌ {package} não encontrado")
            missing_packages.append(package)

    return len(missing_packages) == 0

def check_app_structure():
    """Verifica estrutura do app.py"""
    print("\n🏗️ Verificando estrutura do app.py...")

    app_file = Path("app.py")
    if not app_file.exists():
        print("❌ app.py não encontrado")
        return False

    with open(app_file, 'r') as f:
        content = f.read()

    required_imports = [
        "import streamlit",
        "from supabase_client",
        "def main()"
    ]

    missing_elements = []
    for element in required_imports:
        if element in content:
            print(f"✅ {element}")
        else:
            print(f"❌ {element} não encontrado")
            missing_elements.append(element)

    # Verificar se não há referências ao Render
    if "render.com" in content.lower():
        print("⚠️ Ainda há referências ao Render no app.py")
        missing_elements.append("Referências ao Render")
    else:
        print("✅ Sem referências ao Render")

    return len(missing_elements) == 0

def check_supabase_config():
    """Verifica arquivos de configuração Supabase"""
    print("\n🔧 Verificando configuração Supabase...")

    # Verificar se há template de environment
    env_files = [
        ".env.supabase",
        ".env",
        ".env.example"
    ]

    has_env = any(Path(f).exists() for f in env_files)

    if has_env:
        print("✅ Arquivo de ambiente encontrado")
        # Verificar conteúdo
        for env_file in env_files:
            if Path(env_file).exists():
                with open(env_file, 'r') as f:
                    content = f.read()

                required_vars = [
                    "SUPABASE_URL",
                    "SUPABASE_ANON_KEY"
                ]

                for var in required_vars:
                    if var in content:
                        print(f"  ✅ {var} configurado")
                    else:
                        print(f"  ❌ {var} não configurado")
    else:
        print("❌ Nenhum arquivo de ambiente encontrado")
        return False

    return True

def generate_test_script():
    """Gera script para testar imports"""
    test_script = '''#!/usr/bin/env python3
"""
Test Imports - AVALIA
Testa se todos os imports funcionam corretamente
"""

try:
    print("📚 Testando imports...")

    # Test streamlit
    import streamlit as st
    print("✅ streamlit importado")

    # Test supabase
    try:
        from supabase import create_client
        print("✅ supabase importado")
    except ImportError:
        print("⚠️ supabase não encontrado, instale com: pip install supabase")

    # Test requests
    import requests
    print("✅ requests importado")

    # Test pandas
    import pandas as pd
    print("✅ pandas importado")

    # Test dotenv
    from dotenv import load_dotenv
    print("✅ dotenv importado")

    # Test local imports
    try:
        from supabase_client import get_supabase_client
        print("✅ supabase_client importado")
    except ImportError as e:
        print(f"⚠️ supabase_client não encontrado: {e}")

    print("\\n✅ Todos os imports básicos funcionam!")
    print("🚀 Execute: streamlit run app.py para iniciar a aplicação")

except Exception as e:
    print(f"❌ Erro nos imports: {e}")
    sys.exit(1)
'''

    with open("test_imports.py", 'w') as f:
        f.write(test_script)

    print("✅ Script 'test_imports.py' criado")

def create_quick_commands():
    """Cria arquivo de comandos rápidos"""
    commands = '''# AVALIA - Comandos Rápidos

## Instalar Dependências
pip install -r requirements.txt

## Testar Imports
python test_imports.py

## Iniciar Aplicação (desenvolvimento)
streamlit run app.py

## Validar Configuração Supabase
python validate_supabase_setup.py

## Obter Ajuda para Credenciais
python get_supabase_info.py

## Verificar Arquivos
python test_local_setup.py
'''

    with open("QUICK_COMMANDS.md", 'w') as f:
        f.write(commands)

    print("✅ Arquivo 'QUICK_COMMANDS.md' criado")

def main():
    """Função principal"""
    print("🧪 AVALIA - Teste de Configuração Local")
    print("=" * 50)

    # Executar verificações
    files_ok, missing_files = check_files()
    requirements_ok = check_requirements()
    structure_ok = check_app_structure()
    supabase_ok = check_supabase_config()

    # Gerar scripts auxiliares
    print("\n📝 Gerando scripts auxiliares...")
    generate_test_script()
    create_quick_commands()

    # Resumo
    print("\n📊 Resumo da Verificação")
    print("=" * 30)

    checks = [
        ("Arquivos necessários", files_ok),
        ("Requirements", requirements_ok),
        ("Estrutura app.py", structure_ok),
        ("Configuração Supabase", supabase_ok)
    ]

    passed = 0
    total = len(checks)

    for check_name, passed_check in checks:
        status = "✅ PASS" if passed_check else "❌ FAIL"
        print(f"{check_name:20} {status}")
        if passed_check:
            passed += 1

    print(f"\nResultado: {passed}/{total} testes passaram")

    if missing_files:
        print(f"\n⚠️ Arquivos faltando: {', '.join(missing_files)}")

    if passed == total:
        print("\n🎉 Configuração local está pronta!")
        print("\n📋 Próximos passos:")
        print("1. Configure suas credenciais Supabase:")
        print("   python get_supabase_info.py")
        print("2. Teste os imports:")
        print("   python test_imports.py")
        print("3. Execute a aplicação:")
        print("   streamlit run app.py")
    else:
        print("\n⚠️ Corrija os problemas acima antes de continuar")

    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)