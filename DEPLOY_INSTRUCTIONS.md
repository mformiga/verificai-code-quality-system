# AVALIA - Deploy para Produção

## ✅ Status: Pronto para Deploy!

Sua aplicação está funcionando localmente. Hora de ir para produção!

---

## 🚀 Opção 1: Streamlit Cloud (Recomendado)

### 1. Preparar GitHub
```bash
git add .
git commit -m "feat: complete Supabase integration ready for production"
git push origin main
```

### 2. Streamlit Cloud Setup
1. Vá para: https://cloud.streamlit.io
2. **New app** → **From GitHub**
3. **Repository**: verificai-code-quality-system
4. **Branch**: main (ou streamlit-version)
5. **Main file path**: `app.py`
6. **Python version**: 3.11

### 3. Configurar Secrets
Em **Settings → Secrets**, adicione:

```toml
[supabase]
SUPABASE_URL = "https://jjxmfidggofuaxcdtkrd.supabase.co"
SUPABASE_ANON_KEY = "SUA_ANON_KEY_REAL"
SUPABASE_SERVICE_ROLE_KEY = "SUA_SERVICE_ROLE_KEY_REAL"
SUPABASE_PROJECT_REF = "jjxmfidggofuaxcdtkrd"
```

### 4. Deploy!
Clique em **Deploy!** 🚀

---

## 🌐 Opção 2: Outras Plataformas

### Railway
1. Conectar GitHub
2. Configurar variáveis de ambiente
3. Deploy automático

### Heroku
1. Criar app
2. Setar buildpack para Python
3. Configurar secrets
4. Push para deploy

### VPS (DigitalOcean, AWS, etc.)
```bash
# Instalar dependências
pip install -r requirements.txt

# Iniciar com systemd ou forever
streamlit run app.py --server.port 80
```

---

## 🔧 Configurações de Produção

### Environment Variables
```bash
# Production
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_SERVER_ENABLECORS=true
```

### Requirements Adicionais
```txt
# Para produção
gunicorn>=21.0.0
psycopg2-binary>=2.9.0
```

---

## 📊 Monitoramento

### Logs
```bash
# Streamlit Cloud: Dashboard → Logs
# VPS: journalctl -u streamlit
```

### Health Check
```bash
curl https://seu-app.streamlit.app/_stcore/health
```

---

## 🎯 Domínio Personalizado (Opcional)

### Streamlit Cloud
1. Settings → Advanced → Custom domain
2. Adicionar DNS CNAME: `seu-dominio.com → cname.streamlit.app`

### Cloudflare (Recomendado)
1. Adicionar site ao Cloudflare
2. Configurar SSL/TLS
3. Page Rules para redirecionamento

---

## 🔒 Segurança Produção

### Supabase
- ✅ RLS já ativo
- ✅ Buckets privados
- ✅ Autenticação ativa

### Streamlit
- ✅ Variáveis em secrets
- ✅ Não expor credenciais
- ✅ HTTPS automático

---

## 📈 Analytics (Opcional)

```python
# Adicionar ao app.py
import streamlit as st

# Google Analytics
st.markdown("""
<!-- Global site tag (gtag.js) - Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_TRACKING_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_TRACKING_ID');
</script>
""", unsafe_allow_html=True)
```

---

## ✅ Checklist Final

Antes de ir para produção:

- [x] App funciona localmente
- [x] Todos os testes manuais passaram
- [x] Credenciais Supabase ok
- [x] Storage buckets criados
- [x] Push para GitHub
- [ ] Configurar secrets na plataforma
- [ ] Testar em staging (se possível)
- [ ] Deploy para produção
- [ ] Testar produção completa
- [ ] Configurar domínio (opcional)
- [ ] Adicionar analytics (opcional)

---

## 🎉 Parabéns!

Seu sistema AVALIA está pronto para produção!

**Features disponíveis:**
- 🎯 Análise de código automatizada
- 👥 Sistema de usuários
- 📁 Upload e storage
- 📊 Histórico e relatórios
- 🔒 Segurança com RLS
- 🚀 Deploy com 1 clique

**URL esperada**: https://seu-app.streamlit.app

**Sucesso total!** 🚀🎊