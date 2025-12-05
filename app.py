"""
AVALIA - Sistema de Análise de Código Quality
Interface Streamlit para análise automatizada de código
"""

import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime
import os

# Configuração da página
st.set_page_config(
    page_title="AVALIA - Análise de Código",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constantes
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")

# Configuração de CSS para cores AVALIA
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #FFD700, #FFA500);
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        color: #1a1a1a;
        margin-bottom: 2rem;
    }
    .ia-highlight {
        color: #FFD700;
        font-weight: bold;
    }
    .stButton>button {
        background: linear-gradient(90deg, #FFD700, #FFA500);
        color: #1a1a1a;
        border: none;
        font-weight: bold;
    }
    .criteria-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #FFD700;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

def load_criteria():
    """Carrega critérios de análise da API"""
    try:
        response = requests.get(f"{API_BASE_URL}/general-analysis/criteria-working")
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"Erro ao carregar critérios: {e}")

    # Critérios de fallback
    return [
        {"id": "criteria_66", "text": "Princípios SOLID: Analisar violações do SRP e DI", "active": True},
        {"id": "criteria_67", "text": "Acoplamento a Frameworks: Detectar dependências específicas", "active": True},
        {"id": "criteria_68", "text": "Violação de Camadas: Verificar organização arquitetural", "active": True},
        {"id": "criteria_69", "text": "Pressão sobre Memória: Analisar uso de recursos", "active": True},
        {"id": "criteria_70", "text": "Ciclo de Recursos: Gerenciamento de conexões e arquivos", "active": True},
        {"id": "criteria_71", "text": "I/O Bloqueantes: Configurar timeouts e limites", "active": True},
        {"id": "criteria_72", "text": "Dados em Larga Escala: Usar streaming quando necessário", "active": True},
        {"id": "criteria_73", "text": "Condições de Corrida: Transações em operações concorrentes", "active": True},
        {"id": "criteria_74", "text": "Validação de Entradas: DTOs e filtros de segurança", "active": True},
        {"id": "criteria_75", "text": "Acesso a Recursos: Prevenir Path Traversal", "active": True},
        {"id": "criteria_76", "text": "Tratamento de Erros: Evitar catches vazios", "active": True},
        {"id": "criteria_77", "text": "Consistência de API: Contratos de retorno padronizados", "active": True}
    ]

def analyze_code(code_content, file_path, selected_criteria):
    """Analisa código usando a API"""
    try:
        payload = {
            "code_content": code_content,
            "file_path": file_path,
            "selected_criteria": selected_criteria
        }

        response = requests.post(
            f"{API_BASE_URL}/general-analysis/analyze",
            json=payload,
            timeout=300  # 5 minutos timeout
        )

        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Erro na API: {response.status_code} - {response.text}")
            return None

    except Exception as e:
        st.error(f"Erro ao analisar código: {e}")
        return None

def display_criteria_selection(criteria_list):
    """Mostra seleção de critérios"""
    st.subheader("🎯 Critérios de Análise")

    # Select all/none buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Selecionar Todos", key="select_all"):
            st.session_state.selected_criteria = [c["id"] for c in criteria_list]
    with col2:
        if st.button("❌ Desmarcar Todos", key="deselect_all"):
            st.session_state.selected_criteria = []

    # Initialize session state
    if "selected_criteria" not in st.session_state:
        st.session_state.selected_criteria = [c["id"] for c in criteria_list if c.get("active", True)]

    # Criteria checkboxes in columns
    selected = []
    cols = st.columns(2)

    for i, criterion in enumerate(criteria_list):
        with cols[i % 2]:
            # Create a more readable criterion text
            display_text = criterion["text"].split(":")[0] + ":" + criterion["text"].split(":")[1][:80] + "..."

            is_checked = st.checkbox(
                display_text,
                value=criterion["id"] in st.session_state.selected_criteria,
                key=f"criteria_{criterion['id']}"
            )

            if is_checked:
                selected.append(criterion["id"])

    st.session_state.selected_criteria = selected

    # Show count
    st.info(f"📊 {len(selected)} critérios selecionados de {len(criteria_list)} disponíveis")

    return selected

def main():
    """Função principal"""

    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🔍 AVAL<span class="ia-highlight">IA</span> - Análise de Código Quality</h1>
        <p>Sistema inteligente para análise automatizada de qualidade de código</p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.title("⚙️ Configurações")

        # API URL
        api_url = st.text_input(
            "URL da API",
            value=API_BASE_URL,
            help="Endereço da API de análise"
        )

        # Mode selection
        st.subheader("🎯 Modo de Análise")
        analysis_mode = st.radio(
            "Selecione o modo:",
            ["Análise Rápida", "Análise Completa", "Análise Personalizada"]
        )

    # Main content
    tab1, tab2, tab3 = st.tabs(["📝 Análise", "📊 Resultados", "📚 Histórico"])

    with tab1:
        # Load criteria
        with st.spinner("Carregando critérios de análise..."):
            criteria = load_criteria()

        if criteria:
            # Criteria selection
            selected_criteria = display_criteria_selection(criteria)

            # Code input
            st.subheader("💻 Código para Análise")

            # File upload
            uploaded_file = st.file_uploader(
                "Upload de arquivo",
                type=['py', 'js', 'ts', 'java', 'cpp', 'c', 'php', 'rb', 'go'],
                help="Envie arquivos de código fonte para análise"
            )

            # Code input options
            code_input_method = st.radio(
                "Como deseja fornecer o código?",
                ["Upload de Arquivo", "Texto Direto", "Exemplo"]
            )

            code_content = ""
            file_path = ""

            if code_input_method == "Upload de Arquivo" and uploaded_file:
                code_content = uploaded_file.getvalue().decode("utf-8")
                file_path = uploaded_file.name
                st.success(f"📁 Arquivo carregado: {file_path}")

            elif code_input_method == "Texto Direto":
                code_content = st.text_area(
                    "Cole seu código aqui:",
                    height=300,
                    help="Cole o código que deseja analisar"
                )
                file_path = st.text_input("Nome do arquivo (ex: exemplo.py)", value="codigo.py")

            elif code_input_method == "Exemplo":
                example_code = '''
def calculate_total(items):
    """Calculate total with discount"""
    total = 0
    for item in items:
        total += item.price

    # Apply discount
    if total > 100:
        total = total * 0.9

    return total

class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email
        self.password = "123456"  # Bad practice!

    def save_to_db(self):
        import sqlite3
        conn = sqlite3.connect("users.db")
        # SQL injection vulnerability!
        conn.execute(f"INSERT INTO users VALUES ('{self.name}', '{self.email}')")
        conn.commit()
        conn.close()
        '''
                code_content = st.text_area("Código de exemplo:", value=example_code, height=300)
                file_path = "example.py"

            # Display code preview
            if code_content:
                with st.expander("👁️ Visualizar Código"):
                    st.code(code_content, language=language_from_extension(file_path))

            # Analysis button
            if st.button("🚀 Iniciar Análise", type="primary", disabled=not code_content or not selected_criteria):
                with st.spinner("🔍 Analisando código... Isso pode levar alguns minutos."):
                    result = analyze_code(code_content, file_path, selected_criteria)

                    if result:
                        st.session_state.last_analysis = result
                        st.session_state.analysis_timestamp = datetime.now()
                        st.success("✅ Análise concluída!")
                        st.rerun()

    with tab2:
        # Results display
        if "last_analysis" in st.session_state:
            result = st.session_state.last_analysis

            st.subheader("📊 Resultados da Análise")

            # Analysis info
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Arquivo", result.get("file_path", "N/A"))
            with col2:
                st.metric("Critérios", len(result.get("criteria_results", [])))
            with col3:
                if "analysis_timestamp" in st.session_state:
                    st.metric("Data/Hora", st.session_state.analysis_timestamp.strftime("%H:%M:%S"))

            # Criteria results
            criteria_results = result.get("criteria_results", [])

            if criteria_results:
                st.subheader("🎯 Análise por Critério")

                for criterion_result in criteria_results:
                    criterion_id = criterion_result.get("criterion_id", "Unknown")
                    analysis_text = criterion_result.get("analysis_text", "No analysis")
                    violations = criterion_result.get("violations", [])

                    with st.expander(f"📋 {criterion_id} ({len(violations)} ocorrências)"):
                        st.write(f"**Análise:** {analysis_text}")

                        if violations:
                            for i, violation in enumerate(violations, 1):
                                st.markdown(f"**{i}.** {violation}")
                        else:
                            st.success("✅ Nenhuma violação encontrada")
            else:
                st.warning("⚠️ Nenhum resultado de critério encontrado")

            # Summary
            total_violations = sum(len(cr.get("violations", [])) for cr in criteria_results)
            if total_violations > 0:
                st.error(f"🚨 Encontradas {total_violations} possíveis violações no código")
            else:
                st.success("🎉 Código aprovado em todos os critérios analisados!")

        else:
            st.info("📝 Nenhuma análise realizada ainda. Vá para a aba 'Análise' para começar.")

    with tab3:
        # History (simplified for now)
        st.subheader("📚 Histórico de Análises")
        st.info("🚧 Funcionalidade de histórico em desenvolvimento. As análises ficam disponíveis durante a sessão atual.")

def language_from_extension(filename):
    """Get language from file extension"""
    ext = filename.lower().split('.')[-1]
    language_map = {
        'py': 'python',
        'js': 'javascript',
        'ts': 'typescript',
        'java': 'java',
        'cpp': 'cpp',
        'c': 'c',
        'php': 'php',
        'rb': 'ruby',
        'go': 'go',
        'html': 'html',
        'css': 'css',
        'sql': 'sql'
    }
    return language_map.get(ext, 'text')

if __name__ == "__main__":
    main()