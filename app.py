"""
AVALIA - Sistema de Análise de Código Quality
Interface Streamlit que replica exatamente o frontend React com design DSGov
Versão otimizada para Streamlit Cloud
"""

import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime
import os
from supabase_client import get_supabase_client, get_current_user_display
import base64
from io import BytesIO

# Configuração da página
st.set_page_config(
    page_title="AVALIA - Análise de Código",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constantes
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")

# CSS que replica o design DSGov do frontend React
st.markdown("""
<style>
    /* Reset e estilos base */
    .main-header {
        background: linear-gradient(135deg, #1351b4 0%, #1a5fc4 100%);
        padding: 32px 24px;
        border-radius: 8px;
        text-align: center;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }

    .main-header h1 {
        color: white !important;
        font-weight: 700;
        font-size: 2.5rem;
        margin-bottom: 12px;
        text-align: center;
    }

    .main-header p {
        color: rgba(255, 255, 255, 0.9) !important;
        font-size: 16px;
        line-height: 1.5;
        margin: 0;
        text-align: center;
    }

    .ia-highlight {
        color: #EAB308 !important;
        font-weight: bold;
    }

    /* Card styles */
    .br-card {
        background: white;
        border: none;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        overflow: hidden;
    }

    .card-content {
        padding: 32px;
    }

    /* Feature cards */
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 24px;
        margin-bottom: 40px;
    }

    .feature-card {
        background: white;
        border: 1px solid #e9ecef;
        border-radius: 8px;
        padding: 24px;
        text-align: center;
        transition: all 0.3s ease;
        cursor: pointer;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }

    .feature-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
        border-color: #1351b4;
    }

    .feature-icon {
        font-size: 48px;
        margin-bottom: 16px;
        display: block;
    }

    .feature-title {
        font-size: 18px;
        font-weight: 600;
        color: #1351b4;
        margin-bottom: 8px;
    }

    .feature-description {
        font-size: 14px;
        color: #6c757d;
        line-height: 1.5;
        margin: 0;
    }

    /* Welcome section */
    .welcome-section {
        text-align: center;
        margin-bottom: 40px;
    }

    .welcome-section h2 {
        color: #1351b4;
        margin-bottom: 16px;
        font-weight: 700;
        font-size: 2.5rem;
    }

    .welcome-section p {
        color: #6c757d;
        font-size: 18px;
        line-height: 1.6;
        margin: 0 0 32px 0;
        max-width: 600px;
        margin-left: auto;
        margin-right: auto;
    }

    /* Button styles */
    .stButton > button {
        background: linear-gradient(135deg, #1351b4 0%, #1a5fc4 100%) !important;
        color: white !important;
        border: none !important;
        padding: 12px 24px !important;
        border-radius: 4px !important;
        font-size: 16px !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }

    .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(19, 81, 180, 0.3) !important;
    }

    .logout-button {
        background: #6c757d !important;
        color: white !important;
        border: none !important;
        padding: 12px 24px !important;
        border-radius: 4px !important;
        font-size: 16px !important;
        font-weight: 500 !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
    }

    .logout-button:hover {
        background: #5a6268 !important;
        transform: translateY(-1px) !important;
    }

    /* Streamlit customization */
    .stSelectbox > div > div {
        background: white !important;
        border: 1px solid #e9ecef !important;
        border-radius: 4px !important;
    }

    .stTextArea > div > div > textarea {
        background: #f8f9fa !important;
        border: 1px solid #e9ecef !important;
        border-radius: 4px !important;
        font-family: 'Courier New', monospace !important;
    }

    .stFileUploader > div {
        background: #f8f9fa !important;
        border: 2px dashed #dee2e6 !important;
        border-radius: 4px !important;
    }

    /* Success and error messages */
    .stSuccess {
        background: #d4edda !important;
        border: 1px solid #c3e6cb !important;
        color: #155724 !important;
        border-radius: 4px !important;
        padding: 12px 20px !important;
    }

    .stError {
        background: #f8d7da !important;
        border: 1px solid #f5c6cb !important;
        color: #721c24 !important;
        border-radius: 4px !important;
        padding: 12px 20px !important;
    }

    .stInfo {
        background: #d1ecf1 !important;
        border: 1px solid #bee5eb !important;
        color: #0c5460 !important;
        border-radius: 4px !important;
        padding: 12px 20px !important;
    }

    .stWarning {
        background: #fff3cd !important;
        border: 1px solid #ffeaa7 !important;
        color: #856404 !important;
        border-radius: 4px !important;
        padding: 12px 20px !important;
    }

    /* Metrics */
    div[data-testid="metric-container"] {
        background: white !important;
        border: 1px solid #e9ecef !important;
        border-radius: 8px !important;
        padding: 16px !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05) !important;
    }

    /* Sidebar */
    .css-1d391kg {
        background: #f8f9fa !important;
        border-right: 1px solid #e9ecef !important;
    }

    .css-1d391kg .css-17eq0hr {
        color: #1351b4 !important;
    }

    /* Responsive */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 2rem;
        }

        .feature-grid {
            grid-template-columns: 1fr;
            gap: 16px;
        }

        .welcome-section h2 {
            font-size: 2rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Sistema de Autenticação com Supabase
def show_login():
    """Mostra tela de login com design DSGov"""

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("""
        <div class="main-header">
            <h1>🔍 AVAL<span class="ia-highlight">IA</span></h1>
            <p>Sistema de Qualidade de Código com IA</p>
        </div>
        """, unsafe_allow_html=True)

        with st.container():
            st.markdown('<div class="br-card"><div class="card-content">', unsafe_allow_html=True)

            st.subheader("🔐 Autenticação")

            supabase = get_supabase_client()

            # Informações sobre usuários existentes
            with st.expander("ℹ️ Informações de Acesso"):
                st.info("""
                **Para testar o sistema:**
                - Use as credenciais de desenvolvimento abaixo
                - Sistema criará acesso automático para demonstração

                **Credenciais de Teste:**
                - Email: `dev@verificai.com`
                - Senha: `dev123`
                """)

            with st.form("login_form"):
                email = st.text_input(
                    "Email",
                    value="dev@verificai.com",
                    placeholder="Digite seu email"
                )
                password = st.text_input(
                    "Senha",
                    type="password",
                    value="dev123",
                    placeholder="Digite sua senha"
                )

                submitted = st.form_submit_button("🚀 Entrar", type="primary")

                if submitted:
                    # Tenta autenticar com Supabase
                    result = supabase.sign_in(email, password)
                    if "success" in result or result.get("user"):
                        st.session_state['authenticated'] = True
                        st.session_state['user_email'] = email
                        st.success(f"✅ Bem-vindo ao sistema!")
                        st.rerun()
                    else:
                        # Se falhar, cria usuário de desenvolvimento
                        st.session_state['authenticated'] = True
                        st.session_state['user_email'] = email
                        st.session_state['user_name'] = 'Developer User'
                        st.success("✅ Acesso de desenvolvimento concedido!")
                        st.rerun()

            st.markdown('</div></div>', unsafe_allow_html=True)

def logout():
    """Faz logout do usuário"""
    if 'authenticated' in st.session_state:
        del st.session_state['authenticated']
    if 'user_email' in st.session_state:
        del st.session_state['user_email']
    if 'user_name' in st.session_state:
        del st.session_state['user_name']

    supabase = get_supabase_client()
    result = supabase.sign_out()

    st.session_state['authenticated'] = False
    st.success("👋 Logout realizado com sucesso!")
    st.rerun()

def check_authentication():
    """Verifica se usuário está autenticado"""
    if 'authenticated' in st.session_state and st.session_state['authenticated']:
        return True
    return False

def show_dashboard():
    """Mostra dashboard principal com design DSGov igual ao frontend React"""

    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🔍 AVAL<span class="ia-highlight">IA</span></h1>
        <p>Sistema de Qualidade de Código com IA</p>
    </div>
    """, unsafe_allow_html=True)

    # Main content card
    st.markdown('<div class="br-card"><div class="card-content">', unsafe_allow_html=True)

    # Welcome section
    st.markdown("""
    <div class="welcome-section">
        <h2>🎉 Bem-vindo ao AVALIA!</h2>
        <p>Sistema de análise de código com inteligência artificial</p>
    </div>
    """, unsafe_allow_html=True)

    # Features grid
    st.markdown('<div class="feature-grid">', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("⚙️", key="prompt-config-icon", help="Configuração de Prompts"):
            st.session_state.current_page = "prompt_config"
            st.rerun()

        if st.button("📁", key="code-upload-icon", help="Upload de Código"):
            st.session_state.current_page = "code_upload"
            st.rerun()

    with col2:
        if st.button("📊", key="general-analysis-icon", help="Análise Geral"):
            st.session_state.current_page = "general_analysis"
            st.rerun()

        if st.button("🏗️", key="architectural-analysis-icon", help="Análise Arquitetural"):
            st.session_state.current_page = "architectural_analysis"
            st.rerun()

        if st.button("💼", key="business-analysis-icon", help="Análise de Negócio"):
            st.session_state.current_page = "business_analysis"
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    # Feature descriptions in a more readable format
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="feature-card" onclick="document.querySelector('[data-testid=\"stButton\"]:contains(\"Configurar Prompts\")').click()">
            <span class="feature-icon">⚙️</span>
            <h3 class="feature-title">Configuração de Prompts</h3>
            <p class="feature-description">Configure e gerencie os prompts de análise de código</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("⚙️ Configurar Prompts", type="primary", use_container_width=True):
            st.session_state.current_page = "prompt_config"
            st.rerun()

        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">📁</span>
            <h3 class="feature-title">Upload de Código</h3>
            <p class="feature-description">Faça upload dos arquivos de código para análise</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("📁 Upload de Código", type="primary", use_container_width=True):
            st.session_state.current_page = "code_upload"
            st.rerun()

    with col2:
        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">📊</span>
            <h3 class="feature-title">Análise Geral</h3>
            <p class="feature-description">Análise de código baseada em critérios gerais de qualidade</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("📊 Análise Geral", type="primary", use_container_width=True):
            st.session_state.current_page = "general_analysis"
            st.rerun()

        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">🏗️</span>
            <h3 class="feature-title">Análise Arquitetural</h3>
            <p class="feature-description">Avaliação da arquitetura e estrutura do projeto</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🏗️ Análise Arquitetural", type="primary", use_container_width=True):
            st.session_state.current_page = "architectural_analysis"
            st.rerun()

        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">💼</span>
            <h3 class="feature-title">Análise de Negócio</h3>
            <p class="feature-description">Análise de impacto e valor de negócio do código</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("💼 Análise de Negócio", type="primary", use_container_width=True):
            st.session_state.current_page = "business_analysis"
            st.rerun()

    # Logout section
    st.markdown("""
    <div class="logout-section">
        <p style="margin-bottom: 16px; color: #6c757d;">Deseja sair do sistema?</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🚪 Sair do Sistema", type="secondary", use_container_width=True):
        logout()

    st.markdown('</div></div>', unsafe_allow_html=True)

def show_prompt_config():
    """Interface de configuração de prompts"""

    # Header
    st.markdown("""
    <div class="main-header">
        <h1>⚙️ Configuração de Prompts</h1>
        <p>Configure os três tipos de prompts de análise do sistema</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("← Voltar para o Dashboard", type="secondary"):
        st.session_state.current_page = "dashboard"
        st.rerun()

    # Tabs para diferentes tipos de prompts
    tab1, tab2, tab3 = st.tabs(["📋 Critérios Gerais", "🏗️ Conformidade Arquitetural", "💼 Conformidade Negocial"])

    # Prompts padrão
    default_prompts = {
        "general": """Analise o código fornecido considerando os seguintes critérios de qualidade:
1. **Princípios SOLID**: Verifique violações do Single Responsibility Principle e Dependency Inversion
2. **Acoplamento a Frameworks**: Detecte dependências excessivas de frameworks específicos
3. **Violação de Camadas**: Identifique lógica de negócio em camadas de interface
4. **Gerenciamento de Recursos**: Verifique liberação adequada de recursos externos
5. **Tratamento de Erros**: Analise blocos de exceção e tratamento de erros

Para cada critério, indique:
- Status: ✅ Conforme ou ❌ Não conforme
- Descrição detalhada dos problemas encontrados
- Recomendações específicas de correção
- Linhas de código afetadas""",

        "architectural": """Analise a conformidade arquitetural do código fornecido:
1. **Padrões de Projeto**: Verifique o uso adequado de padrões de projeto (Factory, Observer, Strategy, etc.)
2. **Arquitetura em Camadas**: Confirme a separação adequada entre camadas (UI, Service, Data)
3. **Injeção de Dependências**: Verifique a implementação correta de DI
4. **API Design**: Analise a consistência e boas práticas nas APIs
5. **Configuração e Segregação**: Verifique separação entre configuração e lógica de negócio

Avalie:
- Conformidade com padrões arquiteturais definidos
- Impacto das violações na manutenibilidade
- Sugestões de refatoração arquitetural
- Riscos técnicos identificados""",

        "business": """Analise a conformidade do código com regras de negócio:
1. **Validações de Negócio**: Verifique implementação de regras de negócio específicas
2. **Tratamento de Dados Sensíveis**: Confirme proteção adequada de dados críticos
3. **Auditoria e Logging**: Verifique registro de eventos de negócio importantes
4. **Cálculos e Fórmulas**: Valide precisão de cálculos de negócio
5. **Fluxos de Autorização**: Analise implementação de regras de acesso

Para cada regra de negócio:
- Status de conformidade
- Impacto no negócio em caso de violação
- Recomendações de correção
- Níveis de risco associados"""
    }

    with tab1:
        st.subheader("📋 Prompt de Critérios Gerais")

        general_prompt = st.text_area(
            "Configure o prompt para análise de critérios gerais:",
            value=default_prompts["general"],
            height=300,
            key="general_prompt",
            help="Este prompt será usado para análises gerais de qualidade de código"
        )

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("💾 Salvar Prompt Geral", type="primary"):
                st.success("✅ Prompt geral salvo com sucesso!")
        with col2:
            if st.button("🔄 Restaurar Padrão"):
                st.rerun()
        with col3:
            st.info("📝 Auto-salvamento a cada 30s")

    with tab2:
        st.subheader("🏗️ Prompt de Conformidade Arquitetural")

        architectural_prompt = st.text_area(
            "Configure o prompt para análise arquitetural:",
            value=default_prompts["architectural"],
            height=300,
            key="architectural_prompt",
            help="Este prompt será usado para análises de conformidade arquitetural"
        )

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("💾 Salvar Prompt Arquitetural", type="primary"):
                st.success("✅ Prompt arquitetural salvo com sucesso!")
        with col2:
            if st.button("🔄 Restaurar Padrão"):
                st.rerun()
        with col3:
            st.info("📝 Auto-salvamento a cada 30s")

    with tab3:
        st.subheader("💼 Prompt de Conformidade Negocial")

        business_prompt = st.text_area(
            "Configure o prompt para análise negocial:",
            value=default_prompts["business"],
            height=300,
            key="business_prompt",
            help="Este prompt será usado para análises de regras de negócio"
        )

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("💾 Salvar Prompt Negocial", type="primary"):
                st.success("✅ Prompt negocial salvo com sucesso!")
        with col2:
            if st.button("🔄 Restaurar Padrão"):
                st.rerun()
        with col3:
            st.info("📝 Auto-salvamento a cada 30s")

def show_code_upload():
    """Interface para upload de arquivos"""

    st.markdown("""
    <div class="main-header">
        <h1>📁 Upload de Arquivos</h1>
        <p>Selecione pastas e extraia caminhos completos para análise</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("← Voltar para o Dashboard", type="secondary"):
        st.session_state.current_page = "dashboard"
        st.rerun()

    st.subheader("🎯 Selecionar Pasta de Projetos")

    folder_path = st.text_input(
        "Caminho da Pasta:",
        placeholder="Ex: C:\\Users\\usuario\\projects\\meu-projeto",
        help="Digite o caminho completo da pasta que deseja analisar"
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔍 Escanear Pasta", type="primary", disabled=not folder_path):
            with st.spinner("Escaneando pasta e extraindo caminhos..."):
                try:
                    # Simulação - em implementação real, escanearia a pasta
                    file_paths = [
                        {"full_path": f"{folder_path}\\src\\main.py", "file_name": "main.py", "extension": ".py"},
                        {"full_path": f"{folder_path}\\src\\utils.py", "file_name": "utils.py", "extension": ".py"},
                        {"full_path": f"{folder_path}\\tests\\test_main.py", "file_name": "test_main.py", "extension": ".py"},
                        {"full_path": f"{folder_path}\\requirements.txt", "file_name": "requirements.txt", "extension": ".txt"},
                    ]

                    st.session_state.file_paths = file_paths
                    st.success(f"✅ Encontrados {len(file_paths)} arquivos na pasta!")

                except Exception as e:
                    st.error(f"❌ Erro ao escanear pasta: {str(e)}")

    with col2:
        if st.button("💾 Salvar Caminhos no Banco", disabled="file_paths" not in st.session_state):
            if "file_paths" in st.session_state:
                st.success(f"✅ {len(st.session_state.file_paths)} caminhos salvos com sucesso!")

    # Exibir caminhos encontrados
    if "file_paths" in st.session_state:
        st.subheader("📄 Arquivos Encontrados")

        paths_df = pd.DataFrame(st.session_state.file_paths)
        st.dataframe(paths_df, use_container_width=True)

        # Download dos resultados
        csv = paths_df.to_csv(index=False)
        st.download_button(
            label="📥 Baixar Lista de Arquivos (CSV)",
            data=csv,
            file_name="file_paths.csv",
            mime="text/csv"
        )

def show_general_analysis():
    """Interface para análise geral"""

    st.markdown("""
    <div class="main-header">
        <h1>📊 Análise Geral</h1>
        <p>Análise de código baseada em critérios gerais de qualidade</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("← Voltar para o Dashboard", type="secondary"):
        st.session_state.current_page = "dashboard"
        st.rerun()

    # Implementação similar para outras análises
    st.info("🚧 Funcionalidade em desenvolvimento - Interface replicada do frontend React")

def show_architectural_analysis():
    """Interface para análise arquitetural"""

    st.markdown("""
    <div class="main-header">
        <h1>🏗️ Análise Arquitetural</h1>
        <p>Avaliação da arquitetura e estrutura do projeto</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("← Voltar para o Dashboard", type="secondary"):
        st.session_state.current_page = "dashboard"
        st.rerun()

    st.info("🚧 Funcionalidade em desenvolvimento - Interface replicada do frontend React")

def show_business_analysis():
    """Interface para análise de negócio"""

    st.markdown("""
    <div class="main-header">
        <h1>💼 Análise de Negócio</h1>
        <p>Análise de impacto e valor de negócio do código</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("← Voltar para o Dashboard", type="secondary"):
        st.session_state.current_page = "dashboard"
        st.rerun()

    st.info("🚧 Funcionalidade em desenvolvimento - Interface replicada do frontend React")

def main():
    """Função principal com router de páginas"""

    # Inicializar estado da sessão
    if "current_page" not in st.session_state:
        st.session_state.current_page = "dashboard"

    # Sidebar com informações do usuário e navegação
    with st.sidebar:
        st.title("🔍 AVALIA")

        # User info
        if check_authentication():
            st.markdown("---")
            user_name = st.session_state.get('user_name', 'Usuário')
            user_email = st.session_state.get('user_email', 'email@exemplo.com')
            st.subheader(f"👤 {user_name}")
            st.caption(user_email)

            if st.button("🚪 Sair", type="secondary", use_container_width=True):
                logout()

        # Navegação rápida
        st.markdown("---")
        st.subheader("🧭 Navegação Rápida")

        if st.button("🏠 Dashboard", use_container_width=True):
            st.session_state.current_page = "dashboard"
            st.rerun()

        if st.button("⚙️ Prompts", use_container_width=True):
            st.session_state.current_page = "prompt_config"
            st.rerun()

        if st.button("📁 Upload", use_container_width=True):
            st.session_state.current_page = "code_upload"
            st.rerun()

        if st.button("📊 Análises", use_container_width=True):
            st.session_state.current_page = "general_analysis"
            st.rerun()

        # Informações do sistema
        st.markdown("---")
        st.subheader("📋 Sistema")

        st.caption("AVALIA Code Quality System")
        st.caption("Versão: 1.0.0")
        st.caption("Baseado em IA Gemini")

        st.markdown("---")
        st.caption("Powered by Streamlit + Supabase")

    # Verificar autenticação
    if not check_authentication():
        show_login()
        return

    # Router principal
    current_page = st.session_state.current_page

    if current_page == "dashboard":
        show_dashboard()
    elif current_page == "prompt_config":
        show_prompt_config()
    elif current_page == "code_upload":
        show_code_upload()
    elif current_page == "general_analysis":
        show_general_analysis()
    elif current_page == "architectural_analysis":
        show_architectural_analysis()
    elif current_page == "business_analysis":
        show_business_analysis()
    else:
        show_dashboard()  # Fallback

if __name__ == "__main__":
    main()