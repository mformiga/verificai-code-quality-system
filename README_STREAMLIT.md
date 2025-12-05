# AVALIA - Versão Streamlit

Interface Streamlit para o sistema de análise de código AVALIA.

## 🚀 Deploy no Streamlit Cloud

### 1. Pré-requisitos
- Conta no Streamlit Cloud (https://share.streamlit.io/)
- Repositório no GitHub com este código

### 2. Configuração do App

1. **Fazer upload para GitHub**:
   ```bash
   git add app.py requirements.txt README_STREAMLIT.md
   git commit -m "feat: add Streamlit version"
   git push origin streamlit-version
   ```

2. **Acessar Streamlit Cloud**:
   - Vá para https://share.streamlit.io/
   - Login com GitHub

3. **Criar Novo App**:
   - Repository: `mformiga/verificai-code-quality-system`
   - Branch: `streamlit-version`
   - Main file path: `app.py`
   - App name: `avalia-streamlit`

### 3. Configurar Variáveis de Ambiente

No Streamlit Cloud, em **Settings → Secrets**, adicionar:

```toml
API_BASE_URL = "http://seu-backend-url:8000/api/v1"
```

### 4. Funcionalidades

- ✅ Interface amigável com design AVALIA
- ✅ Upload de arquivos ou código direto
- ✅ Seleção de critérios de análise
- ✅ Visualização detalhada dos resultados
- ✅ Exemplos para testes rápidos
- ✅ Responsivo e intuitivo

### 5. Linguagens Suportadas

- Python (.py)
- JavaScript (.js)
- TypeScript (.ts)
- Java (.java)
- C/C++ (.c, .cpp)
- PHP (.php)
- Ruby (.rb)
- Go (.go)
- HTML/CSS (.html, .css)
- SQL (.sql)

## 🛠️ Desenvolvimento Local

```bash
# Instalar dependências
pip install -r requirements.txt

# Executar localmente
streamlit run app.py

# Acessar em http://localhost:8501
```

## 📱 Screenshots

A aplicação inclui:

1. **Header com marca AVALIA** - Design amarelo destacado
2. **Sidebar de configurações** - API URL e modo de análise
3. **Tabs organizados**:
   - Análise: Input de código e seleção de critérios
   - Resultados: Visualização detalhada
   - Histórico: Análises anteriores (sessão atual)

## 🔧 Customização

O app está configurado para usar a marca AVALIA com:
- Cores amarelo/laranja (#FFD700, #FFA500)
- Logo 🔍 e elementos visuais consistentes
- Interface responsiva e moderna

## 📞 Suporte

Para dúvidas ou problemas:
- Verifique se o backend está rodando
- Confirme a URL da API está correta
- Revise as variáveis de ambiente no Streamlit Cloud