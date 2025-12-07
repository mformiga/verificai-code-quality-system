# AVALIA - Streamlit + Supabase Deployment Guide

## 🏗️ Architecture Overview
- **Frontend**: React/Vite (Opcional - para interfaces avançadas)
- **Backend**: Streamlit (Principal interface)
- **Database**: Supabase (PostgreSQL + Auth + Storage)
- **Deployment**: Streamlit Cloud

## 📋 Prerequisites
- Conta Supabase (https://app.supabase.com)
- Conta Streamlit Cloud (https://cloud.streamlit.io)
- GitHub repository com código

## 🚀 Deployment Steps

### 1. Configurar Supabase

#### Criar Projeto:
1. Acesse https://app.supabase.com
2. Clique "New Project"
3. Nome: `avalia-code-analysis`
4. Região: escolha a mais próxima
5. Crie senha forte (guarde-anotada!)

#### Executar Schema:
1. No dashboard Supabase → SQL Editor
2. Execute o conteúdo de `supabase_schema_fixed.sql`
3. Execute o conteúdo de `supabase_storage_setup.sql`

#### Obter Credenciais:
1. Project Settings → API
2. Copie:
   - Project URL: `https://PROJECT_REF.supabase.co`
   - anon public key: `eyJhbGciOiJIUzI1NiIs...`
   - service_role key: `eyJhbGciOiJIUzI1NiIs...`

### 2. Configurar Aplicação Streamlit

#### Arquivo `.env`:
```bash
# Supabase Configuration
SUPABASE_URL=https://SEU_PROJECT_REF.supabase.co
SUPABASE_ANON_KEY=SUA_ANON_KEY
SUPABASE_SERVICE_ROLE_KEY=SUA_SERVICE_ROLE_KEY
SUPABASE_PROJECT_REF=SEU_PROJECT_REF

# Database
DATABASE_URL=postgresql://postgres:SUA_SENHA@db.SEU_PROJECT_REF.supabase.co:5432/postgres

# Streamlit
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_SERVER_PORT=8501
```

#### secrets.toml (para Streamlit Cloud):
```toml
[supabase]
SUPABASE_URL = "https://SEU_PROJECT_REF.supabase.co"
SUPABASE_ANON_KEY = "SUA_ANON_KEY"
SUPABASE_SERVICE_ROLE_KEY = "SUA_SERVICE_ROLE_KEY"
SUPABASE_PROJECT_REF = "SEU_PROJECT_REF"

[database]
DATABASE_URL = "postgresql://postgres:SUA_SENHA@db.SEU_PROJECT_REF.supabase.co:5432/postgres"
```

### 3. Deploy no Streamlit Cloud

#### Preparar Repo:
1. Garanta que `app.py` está na raiz
2. Inclua `requirements.txt`
3. Adicione `.streamlit/secrets.toml` (localmente)

#### Deploy:
1. Acesse https://cloud.streamlit.io
2. "New app" → "Deploy from GitHub"
3. Conecte seu repository
4. Configure:
   - Main file path: `app.py`
   - Python version: `3.11`
   - Secrets: adicione as variáveis acima

### 4. Configurar Autenticação

#### Supabase Auth Settings:
1. Dashboard → Authentication → Settings
2. Configure:
   - Site URL: `https://SEU_APP.streamlit.app`
   - Redirect URLs: `https://SEU_APP.streamlit.app/*`
   - Enable email/password signup
   - Disable social providers (não necessários)

#### Frontend Auth (se usar React):
```javascript
// client/src/supabaseClient.js
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

export const supabase = createClient(supabaseUrl, supabaseAnonKey)
```

### 5. Testar Deploy

#### Verificação:
1. Acesse `https://SEU_APP.streamlit.app`
2. Teste registro de usuário
3. Teste upload de arquivos
4. Teste análise de código
5. Verifique logs no Streamlit Cloud

#### Debug:
```bash
# Local testing
streamlit run app.py

# Check logs
tail -f logs/streamlit.log
```

## 📁 Estrutura de Arquivos

```
verificAI-code/
├── app.py                     # App Streamlit principal
├── requirements.txt           # Dependências Python
├── .streamlit/
│   ├── config.toml          # Config Streamlit
│   └── secrets.toml         # Secrets (apenas local)
├── backend/                  # Lógica backend (opcional)
│   └── app/
│       ├── core/
│       │   └── supabase.py  # Integração Supabase
│       └── api/
├── frontend/                 # React app (opcional)
│   ├── src/
│   │   └── supabaseClient.js
│   └── .env.production
├── supabase_schema_fixed.sql # Schema banco
└── supabase_storage_setup.sql # Storage config
```

## 🔧 Configurações Importantes

### Streamlit Config (`.streamlit/config.toml`):
```toml
[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"

[server]
headless = true
port = 8501

[browser]
gatherUsageStats = false
```

### Requirements.txt:
```txt
streamlit>=1.28.0
supabase>=2.0.0
python-dotenv>=1.0.0
pandas>=2.0.0
numpy>=1.24.0
plotly>=5.15.0
```

## 🔒 Segurança

1. **Nunca commitar secrets**
2. **Usar variáveis de ambiente**
3. **Habilitar RLS no Supabase**
4. **Validar inputs do usuário**
5. **Limitar tamanho de uploads**

## 📊 Monitoramento

### Streamlit Cloud:
- Dashboard usage metrics
- Error logs
- Performance metrics

### Supabase:
- Database usage
- Auth events
- Storage usage
- API calls

## 🚨 Troubleshooting

### Common Issues:
1. **Connection refused**: Verificar DATABASE_URL
2. **Auth errors**: Keys incorretas ou RLS bloqueando
3. **Upload fails**: Storage bucket não criado
4. **CORS errors**: Frontend URL não autorizado

### Debug Commands:
```python
# Em app.py
import os
print("SUPABASE_URL:", os.getenv("SUPABASE_URL"))

# Test connection
supabase = get_supabase_client()
print("Supabase client:", supabase)
```

## ✅ Success Checklist

- [ ] Supabase project created
- [ ] Database schema executed
- [ ] Storage buckets created
- [ ] Streamlit app deployed
- [ ] Auth working
- [ ] File uploads working
- [ ] Code analysis working
- [ ] All tests passing

---

**Deployment Ready!** 🎉

Sua aplicação AVALIA estará rodando em:
- **Streamlit**: https://SEU_APP.streamlit.app
- **Supabase**: https://app.supabase.com/project/SEU_PROJECT_REF