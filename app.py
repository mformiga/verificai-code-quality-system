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

# Tenta importar psycopg2, mas não falha se não estiver disponível
try:
    import psycopg2
    POSTGRES_AVAILABLE = True
except ImportError:
    psycopg2 = None
    POSTGRES_AVAILABLE = False

# Detectar ambiente (produção vs local)
def is_production():
    """Detecta se a aplicação está rodando em produção (Streamlit Cloud)"""

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

    # Lógica: Se tem variável de produção OU está no Streamlit Cloud OU não tem arquivo local
    is_prod = env_production or streamlit_cloud or not has_local_env

    # Debug detalhado
    debug_info = {
        'ENVIRONMENT': os.getenv('ENVIRONMENT', 'not_set'),
        'IS_STREAMLIT_CLOUD': os.getenv('IS_STREAMLIT_CLOUD', 'not_set'),
        'FORCE_PRODUCTION': os.getenv('FORCE_PRODUCTION', 'not_set'),
        'STREAMLIT_SHARING': 'present' if streamlit_cloud else 'absent',
        '.env.local': 'exists' if has_local_env else 'absent',
        'is_production': is_prod
    }

    print(f"DETECÇÃO DE AMBIENTE - Debug: {debug_info}")

    return is_prod

# Carregar configuração do Supabase para produção
SUPABASE_AVAILABLE = False
supabase = None

# Debug: Mostrar ambiente detectado
environment_debug = f"Local: {os.getcwd()}, Production: {is_production()}"
print(f"AMBIENTE DETECTADO: {environment_debug}")

if is_production():
    try:
        from supabase import create_client

        # Tentar obter dos secrets do Streamlit primeiro
        try:
            SUPABASE_URL = st.secrets["supabase"]["url"]
            SUPABASE_SERVICE_ROLE_KEY = st.secrets["supabase"]["service_role_key"]
        except:
            # Fallback para variáveis de ambiente
            from dotenv import load_dotenv
            load_dotenv('.env.supabase')
            load_dotenv('.env.production')
            load_dotenv('.env')

            SUPABASE_URL = os.getenv('SUPABASE_URL')
            SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

        print(f"Supabase URL encontrado: {bool(SUPABASE_URL)}")
        print(f"Supabase Key encontrado: {bool(SUPABASE_SERVICE_ROLE_KEY)}")

        if SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY:
            supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
            SUPABASE_AVAILABLE = True
            print("Supabase configurado com sucesso")
            st.info(" Ambiente de Produção detectado - Usando Supabase")
        else:
            print("Configuração Supabase incompleta")
            st.error("Configuração do Supabase incompleta - Verifique variáveis de ambiente")
    except ImportError as e:
        print(f"Erro import Supabase: {e}")
        st.error(" Biblioteca Supabase não disponível")
    except Exception as e:
        print(f"Erro configuração Supabase: {e}")
        st.error(f" Erro ao configurar Supabase: {e}")
else:
    print("Usando ambiente local (PostgreSQL)")
    if not POSTGRES_AVAILABLE:
        st.warning("⚠️ psycopg2 não está disponível. Funcionalidades de banco de dados local estarão limitadas.")

# Importação de supabase_client removida - já está integrado diretamente no app
import base64
from io import BytesIO

# Configuração da página
st.set_page_config(
    page_title="AVALIA - Análise de Código",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuração do tema para evitar erros de widgetBackgroundColor
theme_config = {
    "primaryColor": "#1351b4",
    "backgroundColor": "#ffffff",
    "secondaryBackgroundColor": "#f8f9fa",
    "textColor": "#262730",
    "font": "sans serif",
    "sidebar": {
        "backgroundColor": "#f8f9fa",
        "widgetBackgroundColor": "#ffffff"
    }
}

# Aplicar configuração de tema via CSS
st.markdown(f"""
<style>
    /* Corrigir tema do sidebar */
    .css-1d391kg {{
        background: {theme_config['sidebar']['backgroundColor']} !important;
    }}

    .css-1d391kg .stSelectbox > div > div {{
        background: {theme_config['sidebar']['widgetBackgroundColor']} !important;
    }}

    .css-1d391kg .stTextArea > div > div > textarea {{
        background: {theme_config['sidebar']['widgetBackgroundColor']} !important;
    }}

    .css-1d391kg .stFileUploader > div {{
        background: {theme_config['sidebar']['widgetBackgroundColor']} !important;
    }}
</style>
""", unsafe_allow_html=True)

# Constantes
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")

# Configuração do banco PostgreSQL local
POSTGRES_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': os.getenv('POSTGRES_PORT', '5432'),
    'database': os.getenv('POSTGRES_DB', 'verificai'),
    'user': os.getenv('POSTGRES_USER', 'verificai'),
    'password': os.getenv('POSTGRES_PASSWORD', 'verificai123')
}

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
        padding: 8px 12px !important;
        border-radius: 4px !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
        text-align: center !important;
        white-space: pre-line !important;
        line-height: 1.2 !important;
        min-height: 60px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
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
                    # Cria usuário de desenvolvimento diretamente
                    st.session_state['authenticated'] = True
                    st.session_state['user_email'] = email
                    st.session_state['user_name'] = 'Developer User'
                    st.rerun()

            st.markdown('</div></div>', unsafe_allow_html=True)

def logout():
    """Faz logout do usuário"""
    # Limpa sessão
    for key in ['authenticated', 'user_email', 'user_name']:
        if key in st.session_state:
            del st.session_state[key]

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
    st.markdown('<div class="br-card"><div class="card-content" style="padding: 24px;">', unsafe_allow_html=True)

    # Feature descriptions in compact layout - 3 columns
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("⚙️\nConfigurar Prompts", type="primary", use_container_width=True, key="btn_prompts"):
            st.session_state.current_page = "prompt_config"
            st.rerun()

    with col2:
        if st.button("📁\nUpload de Código", type="primary", use_container_width=True, key="btn_upload"):
            st.session_state.current_page = "code_upload"
            st.rerun()

    with col3:
        if st.button("📊\nAnálise Geral", type="primary", use_container_width=True, key="btn_general"):
            st.session_state.current_page = "general_analysis"
            st.rerun()

    # Second row
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🏗️\nAnálise Arquitetural", type="primary", use_container_width=True, key="btn_architectural"):
            st.session_state.current_page = "architectural_analysis"
            st.rerun()

    with col2:
        if st.button("💼\nAnálise de Negócio", type="primary", use_container_width=True, key="btn_business"):
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

def get_prompts_from_postgres():
    """Obtém prompts do banco PostgreSQL local da tabela prompt_configurations"""
    if not POSTGRES_AVAILABLE:
        st.warning("⚠️ PostgreSQL não disponível. Usando prompts padrão.")
        return None

    try:
        # Conecta ao banco PostgreSQL local
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        cursor = conn.cursor()

        # Query para obter prompts da tabela prompt_configurations
        # Pega prompts específicos por ID conhecido ou o mais recente de cada tipo
        query = """
        WITH ranked_prompts AS (
          SELECT prompt_type, content, updated_at, id, name, user_id,
                 ROW_NUMBER() OVER (
                   PARTITION BY prompt_type
                   ORDER BY
                     CASE WHEN id IN (7) THEN 1 ELSE 2 END ASC,
                     CASE WHEN name LIKE '%Template%' THEN 1 ELSE 2 END ASC,
                     LENGTH(content) DESC,
                     updated_at DESC
                 ) as rn
          FROM prompt_configurations
          WHERE is_active = true
        )
        SELECT prompt_type, content, updated_at, id, name
        FROM ranked_prompts
        WHERE rn = 1
        """

        cursor.execute(query)
        rows = cursor.fetchall()

        if rows:
            prompts = {}
            for row in rows:
                prompt_type, content, updated_at, prompt_id, name = row
                # Convert enum values (GENERAL, ARCHITECTURAL, BUSINESS) to lowercase for UI
                prompt_type_lower = prompt_type.lower() if prompt_type else 'general'
                prompts[prompt_type_lower] = {
                    'content': content,
                    'version': 1,
                    'last_modified': str(updated_at) if updated_at else '',
                    'id': prompt_id,
                    'name': name
                }
            return prompts
        else:
            return None

    except Exception as e:
        st.error(f" Erro ao carregar prompts do banco PostgreSQL: {str(e)}")
        return None
    finally:
        if 'conn' in locals():
            conn.close()

def get_prompts_from_supabase():
    """Obtém prompts do Supabase da tabela prompt_configurations"""
    if not SUPABASE_AVAILABLE or not supabase:
        return None

    try:
        # Tentar obter todos os prompts ativos
        response = supabase.table('prompt_configurations').select('*').eq('is_active', True).execute()

        if response.data and len(response.data) > 0:
            # Verificar se os dados são válidos (têm conteúdo)
            valid_prompts = [p for p in response.data if p.get('content') and p.get('prompt_type')]

            if valid_prompts:
                # Simular a mesma lógica de ranking do PostgreSQL
                prompts_by_type = {}
                for prompt in valid_prompts:
                    prompt_type = prompt.get('prompt_type', '').lower()
                    if prompt_type not in prompts_by_type:
                        prompts_by_type[prompt_type] = []
                    prompts_by_type[prompt_type].append(prompt)

                # Para cada tipo, selecionar o melhor prompt
                prompts = {}
                for prompt_type, type_prompts in prompts_by_type.items():
                    if type_prompts:
                        # Aplicar critérios de seleção
                        best_prompt = None
                        best_score = 0

                        for prompt in type_prompts:
                            score = 0
                            prompt_id = prompt.get('id', 0)
                            name = prompt.get('name', '')
                            content = prompt.get('content', '')

                            # Critério 1: ID 7 tem prioridade
                            if prompt_id == 7:
                                score += 1000

                            # Critério 2: Nome com 'Template' tem prioridade
                            if 'Template' in name:
                                score += 500

                            # Critério 3: Conteúdo mais longo
                            score += len(content)

                            if score > best_score:
                                best_score = score
                                best_prompt = prompt

                        if best_prompt:
                            prompts[prompt_type] = {
                                'content': best_prompt.get('content', ''),
                                'version': 1,
                                'last_modified': best_prompt.get('updated_at', ''),
                                'id': best_prompt.get('id', ''),
                                'name': best_prompt.get('name', '')
                            }

                return prompts if prompts else None
            else:
                # Dados existem mas são inválidos
                return None
        else:
            # Nenhum dado encontrado
            return None

    except Exception as e:
        # Silenciar erro em produção para não quebrar a interface
        if is_production():
            # Em produção, apenas logar o erro e retornar None para usar fallback
            print(f"Erro ao carregar prompts do Supabase (usando fallback): {str(e)}")
            return None
        else:
            # Em desenvolvimento, mostrar o erro
            st.error(f" Erro ao carregar prompts do Supabase: {str(e)}")
            return None

def get_prompts():
    """Função principal que obtém prompts da fonte correta baseada no ambiente"""
    production_env = is_production()

    if production_env:
        # Em produção, usa Supabase
        print(f"AMBIENTE PRODUCAO DETECTADO - Tentando carregar prompts do Supabase...")
        prompts = get_prompts_from_supabase()
        if prompts:
            print(f"[OK] Prompts carregados do Supabase: {list(prompts.keys())}")
            for prompt_type, prompt_data in prompts.items():
                print(f"  - {prompt_type}: {prompt_data['name']} ({len(prompt_data['content'])} chars)")
        else:
            print("[ERRO] Nenhum prompt carregado do Supabase - Usando fallback")
        return prompts
    else:
        # Em desenvolvimento, usa PostgreSQL local
        print(f"AMBIENTE DESENVOLVIMENTO DETECTADO - Tentando carregar prompts do PostgreSQL local...")
        prompts = get_prompts_from_postgres()
        if prompts:
            print(f"[OK] Prompts carregados do PostgreSQL: {list(prompts.keys())}")
            for prompt_type, prompt_data in prompts.items():
                print(f"  - {prompt_type}: {prompt_data['name']} ({len(prompt_data['content'])} chars)")
        else:
            print("[ERRO] Nenhum prompt carregado do PostgreSQL - Usando fallback")
        return prompts

def save_prompt_to_postgres(prompt_type, content):
    """Salva/atualiza um prompt no banco PostgreSQL local na tabela prompt_configurations"""
    if not POSTGRES_AVAILABLE:
        st.error(" PostgreSQL não disponível. Não foi possível salvar o prompt.")
        return False

    try:
        # Conecta ao banco PostgreSQL local
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        cursor = conn.cursor()

        # Converte para maiúsculas para o enum PostgreSQL
        prompt_type_upper = prompt_type.upper()

        # Verifica se já existe um prompt deste tipo para o usuário
        check_query = "SELECT id FROM prompt_configurations WHERE prompt_type = %s AND user_id = 1 AND name = %s"
        cursor.execute(check_query, (prompt_type_upper, f"{prompt_type}_config"))
        existing = cursor.fetchone()

        if existing:
            # Atualiza prompt existente
            prompt_id = existing[0]
            update_query = """
            UPDATE prompt_configurations
            SET content = %s, updated_at = CURRENT_TIMESTAMP, updated_by = 1
            WHERE id = %s
            """
            cursor.execute(update_query, (content, prompt_id))
        else:
            # Cria novo prompt
            insert_query = """
            INSERT INTO prompt_configurations (prompt_type, name, content, user_id, is_active, is_default, created_at, updated_at, created_by, updated_by)
            VALUES (%s, %s, %s, 1, true, false, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 1, 1)
            """
            cursor.execute(insert_query, (prompt_type_upper, f"{prompt_type}_config", content))

        # Commit da transação
        conn.commit()
        return True

    except Exception as e:
        st.error(f" Erro ao salvar prompt no PostgreSQL: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def sync_prompt_to_supabase(prompt_type, content):
    """Sincroniza um prompt com o Supabase remoto via MCP"""
    try:
        global supabase
        if not supabase:
            st.warning("⚠️ Supabase não disponível para sincronização remota")
            return False

        # Verifica se já existe na tabela prompts (legado)
        existing = supabase.table('prompts').select('*').eq('type', prompt_type).execute()

        if existing.data:
            # Atualiza prompt existente
            prompt_id = existing.data[0]['id']
            supabase.table('prompts').update({
                'content': content,
                'updated_at': 'now()'
            }).eq('id', prompt_id).execute()
        else:
            # Cria novo prompt
            supabase.table('prompts').insert({
                'type': prompt_type,
                'content': content,
                'version': 1,
                'created_at': 'now()',
                'updated_at': 'now()'
            }).execute()

        st.success(f" Prompt {prompt_type} sincronizado com Supabase remoto")
        return True
    except Exception as e:
        st.error(f" Erro ao sincronizar prompt com Supabase: {str(e)}")
        return False

def save_prompt_to_supabase(prompt_type, content):
    """Salva/atualiza um prompt no Supabase (legado - manter para compatibilidade)"""
    try:
        global supabase
        if not supabase:
            st.warning("⚠️ Supabase não disponível para salvar prompt")
            return False

        # Verifica se já existe
        existing = supabase.table('prompts').select('*').eq('type', prompt_type).execute()

        if existing.data:
            # Atualiza prompt existente
            prompt_id = existing.data[0]['id']
            supabase.table('prompts').update({
                'content': content,
                'updated_at': 'now()'
            }).eq('id', prompt_id).execute()
        else:
            # Cria novo prompt
            supabase.table('prompts').insert({
                'type': prompt_type,
                'content': content,
                'version': 1,
                'created_at': 'now()',
                'updated_at': 'now()'
            }).execute()

        return True
    except Exception as e:
        st.error(f" Erro ao salvar prompt: {str(e)}")
        return False

def show_prompt_config():
    """Interface de configuração de prompts com integração Supabase"""

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

    # Carregar prompts da fonte correta (PostgreSQL local ou Supabase)
    db_source = "Supabase" if is_production() else "PostgreSQL local"
    with st.spinner(f"Carregando prompts do {db_source}..."):
        saved_prompts = get_prompts()

    # Tabs para diferentes tipos de prompts
    tab1, tab2, tab3 = st.tabs(["📋 Critérios Gerais", "🏗️ Conformidade Arquitetural", "💼 Conformidade Negocial"])

    # Prompts padrão (fallback caso não exista no banco)
    default_prompts = {
        "general": """Analise o código fornecido considerando os seguintes critérios de qualidade:
1. **Princípios SOLID**: Verifique violações do Single Responsibility Principle e Dependency Inversion
2. **Acoplamento a Frameworks**: Detecte dependências excessivas de frameworks específicos
3. **Violação de Camadas**: Identifique lógica de negócio em camadas de interface
4. **Gerenciamento de Recursos**: Verifique liberação adequada de recursos externos
5. **Tratamento de Erros**: Analise blocos de exceção e tratamento de erros

Para cada critério, indique:
- Status:  Conforme ou  Não conforme
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

        # Usa prompt do banco se existir, senão usa padrão
        if saved_prompts and saved_prompts.get('general'):
            general_prompt_value = saved_prompts.get('general', {}).get('content', default_prompts["general"])
        else:
            general_prompt_value = default_prompts["general"]

        general_prompt = st.text_area(
            "Configure o prompt para análise de critérios gerais:",
            value=general_prompt_value,
            height=600,
            key="general_prompt",
            help="Este prompt será usado para análises gerais de qualidade de código"
        )

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("💾 Salvar Prompt Geral", type="primary", key="save_general"):
                if save_prompt_to_postgres('general', general_prompt):
                    st.success(" Prompt geral salvo no banco local!")
                    # Sincronizar com Supabase remoto
                    sync_prompt_to_supabase('general', general_prompt)
        with col2:
            if st.button("🔄 Usar Padrão", key="restore_general"):
                st.session_state[f'general_prompt_temp'] = default_prompts["general"]
                st.rerun()
        with col3:
            if saved_prompts and saved_prompts.get('general'):
                st.info(f"📝 Versão: {saved_prompts['general'].get('version', 1)}")
            else:
                st.info("📝 Auto-salvamento a cada 30s")

    with tab2:
        st.subheader("🏗️ Prompt de Conformidade Arquitetural")

        if saved_prompts and saved_prompts.get('architectural'):
            architectural_prompt_value = saved_prompts.get('architectural', {}).get('content', default_prompts["architectural"])
        else:
            architectural_prompt_value = default_prompts["architectural"]

        architectural_prompt = st.text_area(
            "Configure o prompt para análise arquitetural:",
            value=architectural_prompt_value,
            height=600,
            key="architectural_prompt",
            help="Este prompt será usado para análises de conformidade arquitetural"
        )

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("💾 Salvar Prompt Arquitetural", type="primary", key="save_architectural"):
                if save_prompt_to_postgres('architectural', architectural_prompt):
                    st.success(" Prompt arquitetural salvo no banco local!")
                    # Sincronizar com Supabase remoto
                    sync_prompt_to_supabase('architectural', architectural_prompt)
        with col2:
            if st.button("🔄 Usar Padrão", key="restore_architectural"):
                st.session_state[f'architectural_prompt_temp'] = default_prompts["architectural"]
                st.rerun()
        with col3:
            if saved_prompts and saved_prompts.get('architectural'):
                st.info(f"📝 Versão: {saved_prompts['architectural'].get('version', 1)}")
            else:
                st.info("📝 Auto-salvamento a cada 30s")

    with tab3:
        st.subheader("💼 Prompt de Conformidade Negocial")

        if saved_prompts and saved_prompts.get('business'):
            business_prompt_value = saved_prompts.get('business', {}).get('content', default_prompts["business"])
        else:
            business_prompt_value = default_prompts["business"]

        business_prompt = st.text_area(
            "Configure o prompt para análise negocial:",
            value=business_prompt_value,
            height=600,
            key="business_prompt",
            help="Este prompt será usado para análises de regras de negócio"
        )

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("💾 Salvar Prompt Negocial", type="primary", key="save_business"):
                if save_prompt_to_postgres('business', business_prompt):
                    st.success(" Prompt negocial salvo no banco local!")
                    # Sincronizar com Supabase remoto
                    sync_prompt_to_supabase('business', business_prompt)
        with col2:
            if st.button("🔄 Usar Padrão", key="restore_business"):
                st.session_state[f'business_prompt_temp'] = default_prompts["business"]
                st.rerun()
        with col3:
            if saved_prompts and saved_prompts.get('business'):
                st.info(f"📝 Versão: {saved_prompts['business'].get('version', 1)}")
            else:
                st.info("📝 Auto-salvamento a cada 30s")

    # Seção de informações do banco
    if saved_prompts:
        st.markdown("---")
        st.subheader("📊 Status do Banco de Dados")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Prompts Salvos", len(saved_prompts))
        with col2:
            last_update = max(
                saved_prompts.get('general', {}).get('last_modified', 'N/A'),
                saved_prompts.get('architectural', {}).get('last_modified', 'N/A'),
                saved_prompts.get('business', {}).get('last_modified', 'N/A')
            )
            st.metric("Última Atualização", last_update[:19] if last_update != 'N/A' else 'N/A')
    else:
        st.warning("⚠️ Nenhum prompt encontrado no banco. Use os prompts padrão ou configure novos prompts.")

def get_auth_token():
    """Obtém token de autenticação real fazendo login na API"""
    if 'auth_token' in st.session_state and st.session_state['auth_token']:
        return st.session_state['auth_token']

    # Tenta fazer login com credenciais de desenvolvimento
    try:
        login_data = {
            'username': 'dev',  # Username como definido no backend
            'password': 'Dev123456@'
        }

        response = requests.post(
            f"{API_BASE_URL}/login",
            data=login_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=10
        )

        if response.status_code == 200:
            token_data = response.json()
            if 'access_token' in token_data:
                st.session_state['auth_token'] = token_data['access_token']
                return token_data['access_token']

        st.error(" Falha na autenticação: Credenciais inválidas")
        return None

    except Exception as e:
        st.error(f" Erro de autenticação: {str(e)}")
        return None

def login_streamlit_user():
    """Faz login do usuário Streamlit na API backend"""
    if get_auth_token():
        return True  # Já está autenticado

    # Interface de login
    with st.form("api_login_form"):
        st.subheader("🔐 Login Necessário")
        email = st.text_input(
            "Username",
            value="dev",
            help="Use o username cadastrado no sistema"
        )
        password = st.text_input(
            "Senha",
            type="password",
            value="Dev123456@",
            help="Senha de acesso"
        )

        submitted = st.form_submit_button("🚀 Fazer Login na API", type="primary")

        if submitted:
            try:
                login_data = {
                    'username': email,
                    'password': password
                }

                with st.spinner("Fazendo login..."):
                    response = requests.post(
                        f"{API_BASE_URL}/login",
                        data=login_data,
                        headers={'Content-Type': 'application/x-www-form-urlencoded'},
                        timeout=10
                    )

                if response.status_code == 200:
                    token_data = response.json()
                    if 'access_token' in token_data:
                        st.session_state['auth_token'] = token_data['access_token']
                        st.success(" Login realizado com sucesso!")
                        st.rerun()
                    else:
                        st.error(" Token não encontrado na resposta")
                else:
                    st.error(f" Falha no login: {response.status_code} - {response.text}")

            except Exception as e:
                st.error(f" Erro ao fazer login: {str(e)}")

    return False

def upload_file_to_api(file, file_id=None):
    """Faz upload de um arquivo para a API backend"""
    if file_id is None:
        file_id = f"file_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(file.name)}"

    try:
        # Prepara arquivo para upload
        files = {
            'file': (file.name, file.getvalue(), 'application/octet-stream')
        }

        data = {
            'fileId': file_id,
            'originalName': file.name,
            'relativePath': file.name
        }

        # Faz requisição para a API
        response = requests.post(
            f"{API_BASE_URL}/upload",
            files=files,
            data=data,
            headers={
                'Authorization': f'Bearer {get_auth_token()}'
            },
            timeout=300  # 5 minutos timeout
        )

        if response.status_code == 200:
            return {
                'success': True,
                'data': response.json(),
                'file_id': file_id
            }
        else:
            return {
                'success': False,
                'error': f"Erro {response.status_code}: {response.text}",
                'file_id': file_id
            }

    except Exception as e:
        return {
            'success': False,
            'error': f"Erro de conexão: {str(e)}",
            'file_id': file_id
        }

def save_file_path_to_postgres(file_info):
    """Salva informações do arquivo no PostgreSQL local"""
    if not POSTGRES_AVAILABLE:
        st.warning("PostgreSQL não disponível - arquivo não será salvo no banco local")
        return True  # Não falhar se PostgreSQL não estiver disponível

    try:
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        cursor = conn.cursor()

        # Insere ou atualiza informação do arquivo
        query = """
        INSERT INTO file_paths (full_path, file_name, file_extension, folder_path, file_size, is_processed, user_id, is_public, access_level)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (full_path) DO UPDATE SET
            file_size = EXCLUDED.file_size,
            is_processed = EXCLUDED.is_processed,
            updated_at = CURRENT_TIMESTAMP
        """

        cursor.execute(query, (
            file_info['full_path'],
            file_info['file_name'],
            file_info['file_extension'],
            file_info['folder_path'],
            file_info['file_size'],
            True,  # is_processed
            1,     # user_id (desenvolvimento)
            False, # is_public
            'private'  # access_level
        ))

        conn.commit()
        return True

    except Exception as e:
        st.error(f"Erro ao salvar no PostgreSQL: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def save_text_code(title, description, content, file_extension):
    """Save text-based source code directly to PostgreSQL database"""
    try:
        # Create progress indicators
        progress_bar = st.progress(0)
        status_text = st.empty()

        status_text.text("Validando conteúdo...")
        progress_bar.progress(10)

        # Validate content size
        content_size_bytes = len(content.encode('utf-8'))
        if content_size_bytes > 1024 * 1024 * 1024:  # 1GB
            st.error(" Conteúdo excede o limite de 1GB")
            return

        # Prepare data
        file_name = f"{title.replace(' ', '_').lower()}{file_extension}"

        status_text.text("Salvando no PostgreSQL local...")
        progress_bar.progress(30)

        # Save directly to PostgreSQL
        status_text.text("Conectando ao banco de dados...")
        progress_bar.progress(50)

        success = save_source_code_to_postgres(title, description, content, file_extension)

        status_text.text("Finalizando...")
        progress_bar.progress(80)

        if success:
            progress_bar.progress(100)
            st.success("Código salvo com sucesso no PostgreSQL local!")

            # Calculate metrics for display
            line_count = len(content.splitlines())
            size_mb = content_size_bytes / (1024 * 1024)
            size_percentage = (content_size_bytes / (1024 * 1024 * 1024)) * 100

            # Detect programming language for display
            language_map = {
                '.py': 'Python', '.js': 'JavaScript', '.jsx': 'JavaScript React',
                '.ts': 'TypeScript', '.tsx': 'TypeScript React', '.java': 'Java',
                '.cpp': 'C++', '.c': 'C', '.cs': 'C#', '.go': 'Go',
                '.rs': 'Rust', '.php': 'PHP', '.rb': 'Ruby', '.swift': 'Swift',
                '.kt': 'Kotlin', '.sql': 'SQL', '.html': 'HTML',
                '.css': 'CSS', '.scss': 'SCSS', '.json': 'JSON',
                '.xml': 'XML', '.yaml': 'YAML', '.yml': 'YAML',
                '.md': 'Markdown', '.txt': 'Plain Text', '.sh': 'Shell'
            }
            programming_language = language_map.get(file_extension, 'Unknown')

            # Show saved information
            with st.expander("Informações do Código Salvo", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Título:**", title)
                    st.write("**Nome do Arquivo:**", file_name)
                    st.write("**Extensão:**", file_extension)
                    st.write("**Tamanho:**", f"{content_size_bytes:,} bytes")

                with col2:
                    st.write("**Linhas:**", line_count)
                    st.write("**Linguagem:**", programming_language)
                    st.write("**Status:**", "ativo")
                    st.write("**Banco de Dados:**", "PostgreSQL local")

                if description:
                    st.write("**Descrição:**", description)

                # Show preview
                st.write("**Prévia do código:**")
                preview_lines = content.splitlines()[:10]
                if len(content.splitlines()) > 10:
                    preview_lines.append("... (truncado)")
                st.code('\n'.join(preview_lines), language=file_extension.lstrip('.'))

            # Show size info
            st.info(f"**Informações de Tamanho:** {size_mb:.2f}MB ({size_percentage:.6f}% do limite de 1GB)")

        else:
            st.error("Falha ao salvar código no PostgreSQL local")

    except Exception as e:
        st.error(f"Erro ao salvar código: {str(e)}")
        print(f"Error in save_text_code: {str(e)}")

def save_source_code_to_postgres(title, description, content, file_extension):
    """Save source code to database (PostgreSQL local or Supabase remote)"""
    import uuid
    from datetime import datetime

    # Generate code_id
    code_id = f"code_{uuid.uuid4().hex}"

    # Prepare data
    file_name = f"{title.replace(' ', '_').lower()}{file_extension}"
    line_count = len(content.splitlines())
    character_count = len(content)
    size_bytes = len(content.encode('utf-8'))

    # Detect programming language
    language_map = {
        '.py': 'Python', '.js': 'JavaScript', '.jsx': 'JavaScript React',
        '.ts': 'TypeScript', '.tsx': 'TypeScript React', '.java': 'Java',
        '.cpp': 'C++', '.c': 'C', '.cs': 'C#', '.go': 'Go',
        '.rs': 'Rust', '.php': 'PHP', '.rb': 'Ruby', '.swift': 'Swift',
        '.kt': 'Kotlin', '.sql': 'SQL', '.html': 'HTML',
        '.css': 'CSS', '.scss': 'SCSS', '.json': 'JSON',
        '.xml': 'XML', '.yaml': 'YAML', '.yml': 'YAML',
        '.md': 'Markdown', '.txt': 'Plain Text', '.sh': 'Shell'
    }

    programming_language = language_map.get(file_extension, 'Unknown')

    # Common data structure
    code_data = {
        'code_id': code_id,
        'title': title,
        'description': description,
        'content': content,
        'file_name': file_name,
        'file_extension': file_extension,
        'programming_language': programming_language,
        'line_count': line_count,
        'character_count': character_count,
        'size_bytes': size_bytes,
        'status': 'active',
        'is_public': False,
        'is_processed': False,
        'processing_status': 'pending',
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    }

    # Verificar ambiente e escolher banco de dados correto
    production_env = is_production()

    if production_env and SUPABASE_AVAILABLE:
        # AMBIENTE PRODUÇÃO - Usar Supabase
        print(f"AMBIENTE PRODUÇÃO - Salvando no Supabase: {code_id}")
        try:
            result = supabase.table('source_codes').insert(code_data).execute()
            print(f"[OK] Salvo no Supabase: {code_id}")
            st.success("Codigo salvo no Supabase (producao)")
            return True
        except Exception as e:
            print(f"[ERRO] Erro ao salvar no Supabase: {e}")
            st.error(f"Erro ao salvar no Supabase: {str(e)}")
            return False
    elif POSTGRES_AVAILABLE:
        # AMBIENTE DESENVOLVIMENTO - Usar PostgreSQL local
        print(f"AMBIENTE DESENVOLVIMENTO - Salvando no PostgreSQL local: {code_id}")
        try:
            # Connect to local PostgreSQL
            conn = psycopg2.connect(**POSTGRES_CONFIG)
            cursor = conn.cursor()

            # Insert into source_codes table
            query = """
            INSERT INTO source_codes (
                code_id, title, description, content, file_name, file_extension,
                programming_language, line_count, character_count, size_bytes,
                status, is_public, is_processed, processing_status,
                created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            cursor.execute(query, (
                code_data['code_id'], code_data['title'], code_data['description'],
                code_data['content'], code_data['file_name'], code_data['file_extension'],
                code_data['programming_language'], code_data['line_count'],
                code_data['character_count'], code_data['size_bytes'],
                code_data['status'], code_data['is_public'], code_data['is_processed'],
                code_data['processing_status'],
                datetime.now(), datetime.now()
            ))

            conn.commit()
            cursor.close()
            conn.close()
            print(f"[OK] Salvo no PostgreSQL local: {code_id}")
            st.success("Codigo salvo no PostgreSQL local (desenvolvimento)")
            return True
        except Exception as e:
            print(f"[ERRO] Erro ao salvar no PostgreSQL local: {e}")
            st.error(f"Erro ao salvar no PostgreSQL local: {str(e)}")
            return False
    else:
        banco_tipo = "Supabase" if production_env else "PostgreSQL local"
        print(f"[ERRO] Nenhum banco de dados disponível para ambiente {production_env}")
        st.error(f"{banco_tipo} não disponível")
        return False


def show_code_upload():
    """Interface para upload de arquivos e código em texto via API ou Supabase"""

    st.markdown("""
    <div class="main-header">
        <h1>📁 Upload de Código</h1>
        <p>Faça upload de arquivos ou insira código diretamente para análise</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("← Voltar para o Dashboard", type="secondary"):
        st.session_state.current_page = "dashboard"
        st.rerun()

    # Em produção, usa apenas Supabase - não precisa de autenticação via API
    if is_production():
        st.info("💾 **Modo Produção**: Salvando diretamente no Supabase (não depende do backend API)")
    else:
        # Em desenvolvimento, verifica autenticação na API
        auth_token = get_auth_token()
        if not auth_token:
            st.warning("⚠️ É necessário fazer login na API para fazer upload de arquivos.")
            login_success = login_streamlit_user()
            if not login_success:
                return  # Usuário não está autenticado, mostrar login
        else:
            st.success(f" Autenticado na API backend")

    # Informações suportadas
    supported_extensions = ['js', 'jsx', 'ts', 'tsx', 'py', 'java', 'c', 'cpp', 'h', 'hpp', 'cs', 'go', 'rs', 'rb', 'php', 'swift', 'kt', 'scala', 'm', 'sh', 'bash', 'zsh', 'sql', 'html', 'css', 'scss', 'sass', 'less', 'json', 'xml', 'yaml', 'yml', 'toml', 'ini', 'conf', 'config', 'md', 'txt']

    # Interface com abas para diferentes métodos de upload
    tab1, tab2 = st.tabs(["📝 Inserir Código Texto", "📁 Upload de Arquivos"])

    # Tab 1: Text input
    with tab1:
        st.subheader("📝 Inserir Código Fonte Diretamente")
        st.info("💡 **Limite de tamanho**: PostgreSQL e Supabase suportam até **1GB** de conteúdo de texto por código")

        # Form for text input
        with st.form("text_code_form"):
            # Code metadata
            col1, col2 = st.columns(2)
            with col1:
                code_title = st.text_input(
                    "Título do Código*",
                    placeholder="Ex: Função de validação de usuário",
                    help="Dê um nome descritivo para este trecho de código"
                )

            with col2:
                file_extension = st.selectbox(
                    "Linguagem/Tipo de Arquivo*",
                    options=['.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.cpp', '.c', '.cs', '.go', '.rs', '.php', '.rb', '.swift', '.kt', '.sql', '.html', '.css', '.scss', '.json', '.xml', '.yaml', '.yml', '.md', '.txt', '.sh', '.other'],
                    format_func=lambda x: {
                        '.py': 'Python (.py)', '.js': 'JavaScript (.js)', '.jsx': 'React JSX (.jsx)',
                        '.ts': 'TypeScript (.ts)', '.tsx': 'TypeScript React (.tsx)', '.java': 'Java (.java)',
                        '.cpp': 'C++ (.cpp)', '.c': 'C (.c)', '.cs': 'C# (.cs)', '.go': 'Go (.go)',
                        '.rs': 'Rust (.rs)', '.php': 'PHP (.php)', '.rb': 'Ruby (.rb)', '.swift': 'Swift (.swift)',
                        '.kt': 'Kotlin (.kt)', '.sql': 'SQL (.sql)', '.html': 'HTML (.html)',
                        '.css': 'CSS (.css)', '.scss': 'SCSS (.scss)', '.json': 'JSON (.json)',
                        '.xml': 'XML (.xml)', '.yaml': 'YAML (.yaml)', '.yml': 'YAML (.yml)',
                        '.md': 'Markdown (.md)', '.txt': 'Texto (.txt)', '.sh': 'Shell Script (.sh)',
                        '.other': 'Outro'
                    }.get(x, x)
                )

            code_description = st.text_area(
                "Descrição (opcional)",
                placeholder="Descreva o que este código faz, seu propósito, etc.",
                height=80
            )

            # Code content
            st.markdown("####  Conteúdo do Código Fonte")
            code_content = st.text_area(
                "Cole ou digite seu código aqui*",
                placeholder="def exemplo():\n    # Seu código aqui\n    pass",
                height=400,
                help="Insira o código completo que deseja analisar. O sistema detectará automaticamente a linguagem."
            )

            # Show content statistics
            if code_content:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Linhas", len(code_content.splitlines()))
                with col2:
                    size_bytes = len(code_content.encode('utf-8'))
                    st.metric("Tamanho", f"{size_bytes:,} bytes")
                with col3:
                    size_mb = size_bytes / (1024 * 1024)
                    limit_1gb = 1024  # 1GB in MB
                    percentage = (size_mb / limit_1gb) * 100
                    st.metric("Uso do limite", f"{percentage:.6f}%")

                # Size warning
                if size_mb > 100:  # Warning if larger than 100MB
                    st.warning(f"⚠️ Conteúdo grande: {size_mb:.1f}MB. Considere dividir em partes menores para melhor performance.")

            submitted = st.form_submit_button("🚀 Salvar Código", type="primary")

            if submitted:
                if not code_title or not code_content:
                    st.error(" Preencha todos os campos obrigatórios (Título e Conteúdo)")
                else:
                    save_text_code(code_title, code_description, code_content, file_extension)

    # Tab 2: File upload
    with tab2:
        st.subheader("📤 Upload de Arquivos de Código")

        if is_production():
            st.info(f"📋 **Modo Produção**: Use a aba 'Inserir Código Texto' para adicionar código diretamente ao Supabase")
            st.info("📋 **Formatos suportados**: {', '.join(supported_extensions[:10])}... (máx 1GB por arquivo)")
        else:
            st.info(f"📋 **Formatos suportados**: {', '.join(supported_extensions[:10])}... (máx 50MB por arquivo)")

        # Upload de arquivos
        if not is_production():
            st.info("ℹ️ **Importante**: Para upload de diretórios inteiros com subpastas, use a versão React em http://localhost:3012/code-upload")

            uploaded_files = st.file_uploader(
                "Selecione arquivos para upload (limitado a arquivos individuais):",
                accept_multiple_files=True,
                type=None,  # Permite qualquer tipo, validaremos depois
                help="⚠️ **Limitação do Streamlit**: Upload de diretórios inteiros com subpastas não é suportado. Use a versão React (porta 3012) para essa funcionalidade. Aqui você só pode selecionar arquivos individuais."
            )
        else:
            st.info("🚫 **Upload de arquivos desabilitado em produção**: Use a aba 'Inserir Código Texto' para salvar código diretamente no Supabase")
            uploaded_files = []

    if uploaded_files:
        st.subheader(f"📋 {len(uploaded_files)} arquivo(s) selecionado(s)")

        # Validar arquivos
        valid_files = []
        invalid_files = []

        for file in uploaded_files:
            file_extension = file.name.split('.')[-1].lower() if '.' in file.name else ''

            if file_extension in supported_extensions:
                if file.size <= 50 * 1024 * 1024:  # 50MB
                    valid_files.append(file)
                else:
                    invalid_files.append(f"{file.name} (muito grande: {file.size / 1024 / 1024:.1f}MB)")
            else:
                invalid_files.append(f"{file.name} (formato não suportado: .{file_extension})")

        # Mostrar arquivos inválidos
        if invalid_files:
            st.error(f" Arquivos inválidos ignorados:\n" + "\n".join(f"• {f}" for f in invalid_files))

        if valid_files:
            st.success(f" {len(valid_files)} arquivo(s) válido(s) para upload")

            # Botão de upload
            if st.button("🚀 Fazer Upload para API", type="primary", key="upload_files"):
                progress_bar = st.progress(0)
                status_text = st.empty()

                uploaded_results = []
                failed_uploads = []

                for i, file in enumerate(valid_files):
                    # Atualizar progresso
                    progress = (i / len(valid_files))
                    progress_bar.progress(progress)
                    status_text.text(f"Fazendo upload de {file.name}...")

                    # Fazer upload
                    result = upload_file_to_api(file)

                    if result['success']:
                        # Salvar no PostgreSQL local
                        file_info = {
                            'full_path': f"/uploads/{result['file_id']}_{file.name}",
                            'file_name': file.name,
                            'file_extension': f".{file.name.split('.')[-1].lower()}" if '.' in file.name else '',
                            'folder_path': '',
                            'file_size': file.size
                        }

                        # Tentar salvar no PostgreSQL local
                        save_success = save_file_path_to_postgres(file_info)

                        uploaded_results.append({
                            'name': file.name,
                            'size': file.size,
                            'status': ' Sucesso' + (' (salvo no banco)' if save_success else ' (API OK)'),
                            'file_id': result['file_id']
                        })
                    else:
                        failed_uploads.append({
                            'name': file.name,
                            'error': result['error']
                        })

                # Finalizar progresso
                progress_bar.progress(1.0)

                # Mostrar resultados
                if uploaded_results:
                    st.success(f"🎉 Upload concluído! {len(uploaded_results)} arquivo(s) enviado(s) com sucesso!")

                    # Tabela de uploads bem-sucedidos
                    results_df = pd.DataFrame(uploaded_results)
                    st.dataframe(results_df, use_container_width=True)

                if failed_uploads:
                    st.error(f" {len(failed_uploads)} arquivo(s) falharam:")
                    for failed in failed_uploads:
                        st.error(f"• {failed['name']}: {failed['error']}")

    # Seção de arquivos já carregados (apenas em desenvolvimento)
    if not is_production():
        st.markdown("---")
        st.subheader("📊 Status dos Arquivos Carregados")

        # Verificar status da API
        try:
            response = requests.get(f"{API_BASE_URL}/upload", headers={'Authorization': f'Bearer {get_auth_token()}'}, timeout=10)
            if response.status_code == 200:
                files_data = response.json()
                if files_data.get('files'):
                    files_df = pd.DataFrame(files_data['files'])
                    st.dataframe(files_df[['original_name', 'file_size', 'status', 'upload_date']].rename(columns={
                        'original_name': 'Arquivo',
                        'file_size': 'Tamanho',
                        'status': 'Status',
                        'upload_date': 'Data Upload'
                    }), use_container_width=True)
                else:
                    st.info("Nenhum arquivo encontrado na API")
            else:
                st.warning(f"API não respondeu (status: {response.status_code})")
        except Exception as e:
            st.warning(f"Não foi possível conectar à API: {str(e)}")

    # Seção de códigos salvos no banco
    st.markdown("---")
    if is_production():
        st.subheader("📋 Códigos Salvos no Supabase")
    else:
        st.subheader("📋 Códigos Salvos no PostgreSQL Local")

    try:
        if POSTGRES_AVAILABLE:
            # Função para buscar códigos salvos
            def get_saved_codes():
                """Get saved codes from database (Supabase remote or PostgreSQL local)"""
                try:
                    # Try Supabase first if in production and available
                    if SUPABASE_AVAILABLE and is_production():
                        try:
                            response = supabase.table('source_codes').select(
                                "id, code_id, title, description, file_name, file_extension, "
                                "programming_language, line_count, size_bytes, created_at, updated_at"
                            ).eq('status', 'active').order('created_at', desc=True).limit(20).execute()

                            if response.data:
                                # Convert Supabase data to tuple format for compatibility
                                codes = []
                                for item in response.data:
                                    codes.append((
                                        item['id'],
                                        item['code_id'],
                                        item['title'],
                                        item['description'],
                                        item['file_name'],
                                        item['file_extension'],
                                        item['programming_language'],
                                        item['line_count'],
                                        item['size_bytes'],
                                        item['created_at'],
                                        item['updated_at']
                                    ))
                                print(f"Retrieved {len(codes)} codes from Supabase")
                                return codes
                            else:
                                print("No codes found in Supabase")
                                return []
                        except Exception as e:
                            print(f"Error fetching from Supabase: {e}")
                            st.error(f"Erro ao buscar do Supabase: {str(e)}")
                            return []

                    # Fallback to local PostgreSQL
                    elif POSTGRES_AVAILABLE:
                        try:
                            import psycopg2
                            from datetime import datetime

                            conn = psycopg2.connect(**POSTGRES_CONFIG)
                            cursor = conn.cursor()

                            # Query para buscar códigos salvos
                            query = """
                            SELECT id, code_id, title, description, file_name, file_extension,
                                   programming_language, line_count, size_bytes, created_at, updated_at
                            FROM source_codes
                            WHERE status = 'active'
                            ORDER BY created_at DESC
                            LIMIT 20
                            """

                            cursor.execute(query)
                            codes = cursor.fetchall()
                            cursor.close()
                            conn.close()

                            print(f"Retrieved {len(codes)} codes from local PostgreSQL")
                            return codes
                        except Exception as e:
                            print(f"Erro ao buscar códigos do PostgreSQL local: {str(e)}")
                            st.error(f"Erro ao buscar do PostgreSQL local: {str(e)}")
                            return []
                    else:
                        st.error("Nenhum banco de dados disponível para buscar códigos")
                        return []

                except Exception as e:
                    print(f"Erro geral ao buscar códigos: {str(e)}")
                    st.error(f"Erro ao buscar códigos: {str(e)}")
                    return []

            # Função para excluir um código
            def delete_code(code_id):
                """Delete code from database (Supabase remote or PostgreSQL local)"""
                try:
                    # Try Supabase first if in production and available
                    if SUPABASE_AVAILABLE and is_production():
                        try:
                            from datetime import datetime

                            # Soft delete in Supabase
                            response = supabase.table('source_codes').update({
                                'status': 'deleted',
                                'updated_at': datetime.now().isoformat()
                            }).eq('id', code_id).execute()

                            if response.data:
                                print(f"Code deleted from Supabase: {code_id}")
                                return True
                            else:
                                print(f"Failed to delete from Supabase: {code_id}")
                                return False
                        except Exception as e:
                            print(f"Error deleting from Supabase: {e}")
                            st.error(f"Erro ao excluir do Supabase: {str(e)}")
                            return False

                    # Fallback to local PostgreSQL
                    elif POSTGRES_AVAILABLE:
                        try:
                            import psycopg2
                            from datetime import datetime

                            conn = psycopg2.connect(**POSTGRES_CONFIG)
                            cursor = conn.cursor()

                            # Atualizar status para 'deleted' em vez de excluir fisicamente
                            update_query = """
                            UPDATE source_codes
                            SET status = 'deleted', updated_at = %s
                            WHERE id = %s
                            """

                            cursor.execute(update_query, (datetime.now(), code_id))
                            conn.commit()
                            cursor.close()
                            conn.close()

                            print(f"Code deleted from local PostgreSQL: {code_id}")
                            return True
                        except Exception as e:
                            print(f"Error deleting from local PostgreSQL: {e}")
                            st.error(f"Erro ao excluir do PostgreSQL local: {str(e)}")
                            return False
                    else:
                        st.error("Nenhum banco de dados disponível para excluir código")
                        return False

                except Exception as e:
                    print(f"Erro geral ao excluir código: {str(e)}")
                    st.error(f"Erro ao excluir código: {str(e)}")
                    return False

            # Botão para recarregar códigos
            if st.button("Recarregar Códigos", type="secondary"):
                st.rerun()

            # Buscar códigos salvos
            saved_codes = get_saved_codes()

            if saved_codes:
                st.info(f"Encontrados {len(saved_codes)} códigos salvos:")

                # Exibir cada código em um expander
                for i, code in enumerate(saved_codes):
                    with st.expander(f" {code[2]} - {code[6]} ({code[8]} bytes)", expanded=i == 0):
                        col1, col2 = st.columns(2)

                        with col1:
                            st.write("**Título:**", code[2])
                            st.write("**ID do Código:**", code[1])
                            st.write("**Arquivo:**", code[4])
                            st.write("**Linguagem:**", code[6])
                            st.write("**Linhas:**", code[7] if code[7] else "N/A")

                        with col2:
                            st.write("**Tamanho:**", f"{code[8]:,} bytes" if code[8] else "N/A")
                            st.write("**Criado em:**", code[9].strftime("%d/%m/%Y %H:%M") if code[9] else "N/A")
                            st.write("**Atualizado em:**", code[10].strftime("%d/%m/%Y %H:%M") if code[10] else "N/A")
                            st.write("**Status:**", code[11] if len(code) > 11 else "active")

                        if code[3]:  # Descrição
                            st.write("**Descrição:**", code[3])

                        # Botões de ação
                        col_btn1, col_btn2 = st.columns(2)

                        with col_btn1:
                            # Botão para ver o conteúdo completo
                            if st.button(f"Ver Conteúdo Completo", key=f"view_content_{code[0]}"):
                                try:
                                    conn = psycopg2.connect(**POSTGRES_CONFIG)
                                    cursor = conn.cursor()

                                    content_query = """
                                    SELECT content FROM source_codes WHERE id = %s
                                    """
                                    cursor.execute(content_query, (code[0],))
                                    content_result = cursor.fetchone()

                                    if content_result:
                                        content = content_result[0]
                                        st.write("**Conteúdo do Código:**")
                                        st.code(content, language=code[6].lower() if code[6] else "")

                                    cursor.close()
                                    conn.close()
                                except Exception as e:
                                    st.error(f"Erro ao carregar conteúdo: {str(e)}")

                        with col_btn2:
                            # Botão para excluir o código
                            if st.button(f"Excluir Código", key=f"delete_code_{code[0]}", type="secondary"):
                                if st.session_state.get(f"confirm_delete_{code[0]}", False):
                                    # Segunda confirmação
                                    if delete_code(code[0]):
                                        st.success(f"Código '{code[2]}' excluído com sucesso!")
                                        st.rerun()
                                    else:
                                        st.error(f"Erro ao excluir o código '{code[2]}'")
                                else:
                                    # Primeira confirmação
                                    st.session_state[f"confirm_delete_{code[0]}"] = True
                                    st.warning(f"Clique novamente para confirmar a exclusão de '{code[2]}'")
                                    st.rerun()

            else:
                st.info("Nenhum código encontrado no PostgreSQL local.")
                st.write("Use o formulário acima para salvar seu primeiro código!")

        else:
            st.error("PostgreSQL não disponível. Não é possível exibir códigos salvos.")

    except Exception as e:
        st.error(f"Erro ao carregar códigos salvos: {str(e)}")

    # Informações do sistema
    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    with col1:
        if is_production():
            if SUPABASE_AVAILABLE:
                st.metric("Banco de Dados", " Supabase Conectado")
            else:
                st.metric("Banco de Dados", " Supabase Não disponível")
        else:
            if POSTGRES_AVAILABLE:
                st.metric("PostgreSQL", " Conectado")
            else:
                st.metric("PostgreSQL", " Não disponível")

    with col2:
        if is_production():
            st.metric("API Backend", " Não necessário (modo Supabase)")
        else:
            try:
                response = requests.get(f"{API_BASE_URL}/health", timeout=5)
                api_status = " Online" if response.status_code == 200 else " Erro"
                st.metric("API Backend", api_status)
            except:
                st.metric("API Backend", " Offline")

    with col3:
        if is_production():
            st.metric("Upload Max", "1GB (texto)")
        else:
            st.metric("Upload Max", "50MB")

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