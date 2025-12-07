#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste de detecção de ambiente para a aplicação Streamlit
"""

import os
import sys

# Adicionar o diretório atual ao path para importar o app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_environment_detection():
    """Testa a detecção de ambiente em diferentes cenários"""

    print("=== TESTE DE DETECAO DE AMBIENTE ===\n")

    # Salvar valores originais
    original_env = {}
    test_vars = ['ENVIRONMENT', 'IS_STREAMLIT_CLOUD', 'FORCE_PRODUCTION', 'STREAMLIT_SHARING']

    for var in test_vars:
        original_env[var] = os.environ.get(var)

    try:
        # Cenário 1: Ambiente de desenvolvimento (padrão)
        print("CENARIO 1: Ambiente de Desenvolvimento (padrao)")
        print("-" * 50)

        for var in test_vars:
            if var in os.environ:
                del os.environ[var]

        # Importar a função do app após configurar ambiente
        from app import is_production

        result = is_production()
        print(f"Resultado: is_production() = {result}")
        print(f"ENVIRONMENT: {os.getenv('ENVIRONMENT', 'not_set')}")
        print(f"Arquivo .env.local existe: {'Sim' if os.path.exists('.env.local') else 'Não'}")
        print()

        # Cenário 2: Forçar produção
        print("CENARIO 2: Forcar Producao")
        print("-" * 50)

        os.environ['FORCE_PRODUCTION'] = 'true'

        # Recarregar a função para testar novo ambiente
        # Como a função é chamada diretamente, vamos testar o impacto
        result = is_production()
        print(f"Resultado: is_production() = {result}")
        print(f"FORCE_PRODUCTION: {os.getenv('FORCE_PRODUCTION')}")
        print()

        # Cenário 3: Ambiente production
        print("CENARIO 3: Ambiente Production")
        print("-" * 50)

        del os.environ['FORCE_PRODUCTION']
        os.environ['ENVIRONMENT'] = 'production'

        result = is_production()
        print(f"Resultado: is_production() = {result}")
        print(f"ENVIRONMENT: {os.getenv('ENVIRONMENT')}")
        print()

        # Cenário 4: Streamlit Cloud
        print("CENARIO 4: Streamlit Cloud")
        print("-" * 50)

        del os.environ['ENVIRONMENT']
        os.environ['STREAMLIT_SHARING'] = 'true'

        result = is_production()
        print(f"Resultado: is_production() = {result}")
        print(f"STREAMLIT_SHARING: {os.getenv('STREAMLIT_SHARING')}")
        print()

    finally:
        # Restaurar valores originais
        print("Restaurando ambiente original...")
        for var in test_vars:
            if original_env[var] is None:
                if var in os.environ:
                    del os.environ[var]
            else:
                os.environ[var] = original_env[var]

def test_database_functions():
    """Testa as funcoes de banco de dados"""

    print("\n=== TESTE DE FUNCOES DE BANCO DE DADOS ===\n")

    try:
        from app import get_prompts, save_source_code_to_postgres, is_production

        print("Testando get_prompts()...")
        prompts = get_prompts()
        print(f"Resultado: {len(prompts) if prompts else 0} prompts carregados")
        if prompts:
            for key, value in prompts.items():
                print(f"  - {key}: {value.get('name', 'unnamed')}")

        print("\nTestando ambiente de salvamento...")
        production_env = is_production()
        print(f"Ambiente atual: {'Producao (Supabase)' if production_env else 'Desenvolvimento (PostgreSQL local)'}")

    except Exception as e:
        print(f"Erro ao testar funcoes: {e}")

if __name__ == "__main__":
    test_environment_detection()
    test_database_functions()

    print("\n=== RESUMO ===")
    print("Testes concluidos!")
    print("Verifique os logs acima para ver se a deteccao esta funcionando corretamente")
    print("Ajuste as variaveis de ambiente ou crie arquivo .env.local se necessario")