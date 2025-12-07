# 🚀 STREAMLIT CLOUD DEPLOY GUIDE

## ✅ Status Atual
- ✅ Supabase DDL executado com sucesso
- ✅ Tabelas criadas: `source_codes`, `prompt_configurations`
- ✅ RLS configurado
- ✅ Código enviado para GitHub (commit `d4fe9bd`)

## 🔧 PASSO 1: OBTER SERVICE ROLE KEY

### Acesse o Dashboard Supabase:
1. **URL**: https://app.supabase.com/project/jjxmfidggofuaxcdtkrd
2. Clique em **⚙️ Settings** (ícone de engrenagem)
3. Vá para **API**
4. Copie a **Service Role Key** (longa chave secreta)

**A Service Role Key parece com:**
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpqeG1maWRnZ29mdWF4Y2R0a3JkIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczMzc3OTY0MCwiZXhwIjoyMDQ5MzU1NjQwfQ.......
```

## 🔐 PASSO 2: CONFIGURAR STREAMLIT CLOUD

### Opção A: Se já tiver app no Streamlit Cloud
1. **URL**: https://share.streamlit.io/
2. Acesse seu workspace
3. Clique no app existente ou crie novo
4. Vá para **Settings** → **Secrets**
5. Adicione os seguintes secrets:

```toml
# Supabase Configuration
SUPABASE_URL = "https://jjxmfidggofuaxcdtkrd.supabase.co"
SUPABASE_SERVICE_ROLE_KEY = "COLE_A_SERVICE_ROLE_KEY_AQUI"

# Environment
ENVIRONMENT = "production"
```

### Opção B: Criar novo app
1. **New app** → **From existing repo**
2. **Repository**: `mformiga/verificai-code-quality-system`
3. **Branch**: `streamlit-version`
4. **Main file path**: `app.py`
5. **Configure secrets** (mesmo conteúdo acima)

## 🚀 PASSO 3: DEPLOY AUTOMÁTICO

Após configurar os secrets, o build começará automaticamente.

### Monitorar o Deploy:
- **Logs**: clique em "Logs" no app
- **Status**: verifica se está "Running"
- **URL**: será gerada automaticamente

### Logs Esperados:
```
AMBIENTE PRODUCAO DETECTADO - Tentando carregar prompts do Supabase...
Supabase URL encontrado: True
Supabase Key encontrado: True
Supabase configurado com sucesso
[OK] Prompts carregados do Supabase: ['general', 'architectural', 'business']
```

## 🧪 PASSO 4: TESTES PÓS-DEPLOY

### 1. Verificar Funcionalidades:
- ✅ Acessar URL do app
- ✅ Login funcional
- ✅ Configurar prompts (deve carregar do Supabase)
- ✅ Upload de código (deve salvar no Supabase)
- ✅ Listar códigos

### 2. Verificar no Supabase:
1. Dashboard → **Table Editor**
2. Verifique se dados aparecem em `source_codes`
3. Verifique storage bucket

## 🔗 URLS IMPORTANTES

- **Streamlit Cloud**: https://share.streamlit.io/
- **Seu App**: https://[SEU-WORKSPACE].streamlit.app/[SEU-APP]
- **Supabase**: https://app.supabase.com/project/jjxmfidggofuaxcdtkrd
- **GitHub**: https://github.com/mformiga/verificai-code-quality-system

## 🚨 SOLUÇÃO DE PROBLEMAS

### Erro: "Supabase URL não encontrado"
**Solução**: Verifique se SUPABASE_URL está correto nos secrets

### Erro: "Permissão negada"
**Solução**: Verifique se a Service Role Key está completa

### Erro: "Nenhum prompt carregado"
**Solução**:
1. Verifique se a tabela `prompt_configurations` tem dados
2. Verifique logs para ver erros de conexão

### Build falhou:
1. Verifique logs de build
2. Verifique se todos os secrets estão configurados
3. Verifique se o arquivo `app.py` está correto

## ✅ CHECKLIST FINAL

- [ ] Obter Service Role Key do Supabase
- [ ] Configurar secrets no Streamlit Cloud
- [ ] Verificar build automático
- [ ] Testar todas as funcionalidades
- [ ] Confirmar dados salvos no Supabase

---

**Status**: 🚀 **PRONTO PARA DEPLOY!**

Siga os passos acima e sua aplicação estará 100% funcional em produção!