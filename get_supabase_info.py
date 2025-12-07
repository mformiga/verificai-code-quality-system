"""
Get Supabase Project Information
Script para extrair todas as credenciais necessárias do Supabase
"""

import requests
import json
import sys

def get_supabase_info(email, password):
    """
    Extrai informações do projeto Supabase via API web scraping
    Nota: Você precisa fornecer email e senha do Supabase
    """

    print("=" * 60)
    print("AVALIA - Obter Informações do Projeto Supabase")
    print("=" * 60)

    print("\n📋 Para obter suas credenciais Supabase:")
    print("1. Acesse https://app.supabase.com")
    print("2. Faça login com seu email e senha")
    print("3. Crie um novo projeto ou selecione um existente")
    print("4. Vá para Project Settings → API")
    print("5. Copie as informações manualmente (método mais seguro)")

    print("\n" + "=" * 60)
    print("INSTRUÇÕES DETALHADAS:")
    print("=" * 60)

    print("\n🔗 PASSO 1: Acessar o Supabase")
    print("1. Abra seu navegador")
    print("2. Vá para: https://app.supabase.com")
    print("3. Faça login com email e senha")

    print("\n📝 PASSO 2: Criar/Selecionar Projeto")
    print("1. Clique em 'New Project'")
    print("2. Nome: AVALIA Code Analysis")
    print("3. Escolha a região mais próxima")
    print("4. Crie uma senha forte (guarde-anotada!)")
    print("5. Aguarde 2-3 minutos para criação")

    print("\n⚙️  PASSO 3: Obter URL do Projeto")
    print("1. No dashboard do projeto, clique em 'Project Settings'")
    print("2. Copie o 'Project URL'")
    print("3. Exemplo: https://abc123def456.supabase.co")

    print("\n🔑 PASSO 4: Obter Chaves API")
    print("1. Ainda em 'Project Settings', clique em 'API'")
    print("2. Copie a 'anon public key'")
    print("3. Copie a 'service_role key' (se precisar)")

    print("\n📊 PASSO 5: Obter DATABASE_URL")
    print("1. Ainda em 'Project Settings', clique em 'Database'")
    print("2. Copie a 'Connection string'")
    print("3. Formato: postgresql://postgres.iamuser:password@...")

    print("\n" + "=" * 60)
    print("TEMPLATE DE CONFIGURAÇÃO:")
    print("=" * 60)

    template = """
# Cole estas informações no seu .env.supabase ou secrets do Streamlit Cloud:

[supabase]
SUPABASE_URL = "https://SEU_PROJETO_REF.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.SUA_CHAVE_ANON_KEY_AQUI"
SUPABASE_SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.SUA_CHAVE_SERVICE_ROLE_AQUI"
SUPABASE_PROJECT_REF = "SEU_PROJETO_REF"
DATABASE_URL = "postgresql://postgres.iamuser:SUA_SENHA@aws-0-REGION.pooler.supabase.com:5432/postgres"
"""

    print(template)

    print("\n" + "=" * 60)
    print("OBTENDO O PROJECT REF:")
    print("=" * 60)
    print("O Project Ref é a parte do URL antes de '.supabase.co':")
    print("URL: https://abc123def456.supabase.co")
    print("Project Ref: abc123def456")

    return {
        "message": "Siga as instruções acima para obter suas credenciais Supabase"
    }

def create_quick_reference():
    """Cria um arquivo de referência rápida"""

    reference = """
# SUPABASE QUICK REFERENCE - AVALIA

## URL do App (já configurada):
https://verificai-code-quality-system-eapzchsvw6mwarkajltkzf.streamlit.app/

## Onde Configurar no Supabase:
1. Dashboard: https://app.supabase.com
2. Project Settings → API
3. Project Settings → Database

## Informações Necessárias:

### Project URL:
- Formato: https://[PROJECT_REF].supabase.co
- Exemplo: https://abc123def456.supabase.co

### API Keys:
- anon public key (começa com eyJhbGciOiJI...)
- service_role key (começa com eyJhbGciOiJI...)

### Project Ref:
- Parte do URL antes de .supabase.co
- Exemplo: abc123def456

### Database URL:
- Formato: postgresql://postgres.iamuser:[PASSWORD]@[HOST]:5432/postgres
- Encontrado em: Project Settings → Database → Connection string
"""

    with open('supabase_quick_ref.txt', 'w') as f:
        f.write(reference)

    print("✅ Arquivo 'supabase_quick_ref.txt' criado com instruções!")

def main():
    """Função principal"""

    create_quick_reference()

    # Pergunta se o usuário já tem um projeto
    print("\n🤔 Você já tem um projeto Supabase?")
    print("1. Sim - Vá para https://app.supabase.com e siga as instruções")
    print("2. Não - Crie um novo projeto primeiro")

    print("\n📱 Acesso rápido:")
    print("- Dashboard Supabase: https://app.supabase.com")
    print("- Sua aplicação: https://verificai-code-quality-system-eapzchsvw6mwarkajltkzf.streamlit.app/")

    print("\n🎯 Próximos passos:")
    print("1. Configure as credenciais no Streamlit Cloud (Settings → Secrets)")
    print("2. Execute o schema do banco de dados no Supabase SQL Editor")
    print("3. Teste a aplicação!")

    return 0

if __name__ == "__main__":
    try:
        main()
        print("\n✅ Guia criado com sucesso!")
        print("Consulte 'supabase_quick_ref.txt' para instruções detalhadas.")
    except Exception as e:
        print(f"❌ Erro: {e}")
        sys.exit(1)