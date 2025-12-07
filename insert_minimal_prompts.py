#!/usr/bin/env python3
"""
Insert minimal prompts into Supabase - only required fields
"""

import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv('.env.supabase')

try:
    from supabase import create_client
except ImportError as e:
    print(f"Erro de importacao: {e}")
    print("Instale as dependencias com: pip install supabase python-dotenv")
    exit(1)

# Configurações Supabase
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

def create_supabase_client():
    """Create Supabase client"""
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        raise ValueError("Variaveis de ambiente SUPABASE_URL e SUPABASE_SERVICE_ROLE_KEY sao obrigatorias")

    return create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

def get_best_prompt_content():
    """Get the best prompt content from the PostgreSQL local template"""

    # O melhor prompt é o "Template com Código Fonte no Início" (ID: 7)
    best_general_prompt = """Voce e um especialista em analise de codigo.

**INSTRUCAO CRITICA - OBRIGATORIO:**
Para cada criterio de avaliacao abaixo, **SEMPRE** comece sua resposta com:
"### [Nome do Criterio]"

**NUNCA** inclua o codigo fonte no inicio da sua resposta.
O codigo fornecido ja esta visivel para voce e nao deve ser repetido.

Apos cada titulo, forneca uma analise detalhada usando **exemplos especificos** do codigo fornecido.

---

**CRITERIOS DE AVALIACAO:**

### 1. Principios SOLID
- Verifique violacoes do Single Responsibility Principle e Dependency Inversion
- Analise coesao e acoplamento entre classes
- Identifique oportunidades de refatoracao para melhor aderencia aos principios SOLID

### 2. Acoplamento a Frameworks
- Detecte dependencias excessivas de frameworks especificos
- Verifique se o codigo esta preso a tecnologias proprietarias
- Avalie a facilidade de migrar para diferentes frameworks ou plataformas

### 3. Violacao de Camadas
- Identifique logica de negocio em camadas de interface (UI, controllers)
- Verifique acessos diretos a banco de dados em camadas inadequadas
- Analise a separacao adequada entre frontend, backend e camada de dados

### 4. Gerenciamento de Recursos
- Verifique liberacao adequada de recursos externos (conexoes, arquivos, etc.)
- Identifique potenciais memory leaks ou resource leaks
- Analise o uso de patterns como try-finally, using, ou context managers

### 5. Tratamento de Erros
- Analise blocos de excecao e tratamento de erros
- Verifique se ha tratamento adequado de casos excepcionais
- Identifique areas onde erros podem nao estar sendo tratados

**IMPORTANTE:** Para cada criterio, inclua exemplos especificos do codigo fornecido e sugestoes de melhoria concretas."""

    best_architectural_prompt = """Analise o codigo fornecido de uma perspectiva arquitetural:

**Padroes de Design:**
- Verifique o uso adequado de padroes de design GoF
- Identifique oportunidades para aplicar novos padroes
- Avalie a consistencia no uso de padroes existentes

**Principios de Arquitetura:**
- Analise a aderencia a principios como DRY, KISS, YAGNI
- Verifique a modularidade e reusabilidade do codigo
- Avalie a escalabilidade da arquitetura atual

**Organizacao do Codigo:**
- Analise a estrutura de pacotes e modulos
- Verifique a separacao de responsabilidades
- Identifique dependencias circulares ou problematicas

**Sugira melhorias arquiteturais especificas com exemplos praticos.**"""

    best_business_prompt = """Analise o codigo fornecido com foco na logica de negocio:

**Regras de Negocio:**
- Verifique se as regras de negocio estao claramente implementadas
- Identifique validacoes de negocio que podem estar faltando
- Analise a coesao das regras com os requisitos de negocio

**Processos de Negocio:**
- Avalie se os processos de negocio estao bem representados
- Verifique a integracao entre diferentes etapas dos processos
- Identifique gargalos ou ineficiencias nos fluxos de negocio

**Dominio Especifico:**
- Analise se o codigo reflete adequadamente o dominio do problema
- Verifique o uso de linguagem ubiqua e termos de negocio
- Identifique oportunidades de melhor alinhamento com o dominio

**Forneça analise detalhada com exemplos do codigo e sugestoes praticas.**"""

    return {
        'GENERAL': best_general_prompt,
        'ARCHITECTURAL': best_architectural_prompt,
        'BUSINESS': best_business_prompt
    }

def main():
    """Main function"""
    print("Inserindo prompts minimalistas no Supabase...")
    print("=" * 50)

    try:
        supabase = create_supabase_client()
        print("Cliente Supabase criado com sucesso")

        # Obter melhores prompts
        best_prompts = get_best_prompt_content()

        # Criar prompts para inserção (campos necessários)
        prompts_to_insert = [
            {
                'config_name': 'general_analysis',  # Campo necessário
                'prompt_type': 'GENERAL',
                'name': 'Template com Código Fonte no Início',
                'content': best_prompts['GENERAL'],
                'is_active': True,
                'is_default': False
            },
            {
                'config_name': 'architectural_analysis',  # Campo necessário
                'prompt_type': 'ARCHITECTURAL',
                'name': 'Análise Arquitetural Detalhada',
                'content': best_prompts['ARCHITECTURAL'],
                'is_active': True,
                'is_default': False
            },
            {
                'config_name': 'business_analysis',  # Campo necessário
                'prompt_type': 'BUSINESS',
                'name': 'Análise de Negócio Completa',
                'content': best_prompts['BUSINESS'],
                'is_active': True,
                'is_default': False
            }
        ]

        print(f"\nInserindo {len(prompts_to_insert)} prompts...")

        success_count = 0
        for prompt in prompts_to_insert:
            try:
                result = supabase.table('prompt_configurations').insert(prompt).execute()
                if result.data:
                    success_count += 1
                    print(f"[OK] Inserido: {prompt['name']} ({prompt['prompt_type']})")
                    print(f"     ID: {result.data[0]['id']}")
                else:
                    print(f"[ERRO] Falha ao inserir: {prompt['name']}")
            except Exception as e:
                print(f"[ERRO] Erro ao inserir {prompt['name']}: {e}")

        print(f"\nResumo:")
        print(f"Sucesso: {success_count}")
        print(f"Total: {len(prompts_to_insert)}")

        # Verificar resultado
        if success_count > 0:
            print("\nVerificando dados inseridos...")
            result = supabase.table('prompt_configurations').select('*').execute()
            if result.data:
                print(f"Total de prompts no Supabase: {len(result.data)}")
                for prompt in result.data:
                    content_preview = prompt.get('content', '')[:100] + "..." if len(prompt.get('content', '')) > 100 else prompt.get('content', '')
                    print(f"  - {prompt.get('name')} ({prompt.get('prompt_type')})")
                    print(f"    ID: {prompt.get('id')}")
                    print(f"    Content: {content_preview}")
                    print()

    except Exception as e:
        print(f"Erro geral: {e}")

if __name__ == "__main__":
    main()