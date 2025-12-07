# Deploy para Produção - Streamlit Cloud + Render PostgreSQL

## 📋 Status Atual

- ✅ **PostgreSQL Local**: Configurado e funcionando
- ✅ **Prompts**: 3 prompts prontos para sincronização
- ✅ **Render PostgreSQL**: Instance `avalia-db` criada e disponível
- ✅ **Streamlit App**: Funcionalidade de detecção de ambiente implementada

## 🚀 Próximos Passos

### 1. Sincronizar Prompts para PostgreSQL Remoto

**Acesse o Dashboard Render**:
1. Vá para: https://dashboard.render.com/d/dpg-d4p4s5re5dus7381mdug-a
2. Clique em "Query Editor" ou conecte via psql
3. Execute os seguintes comandos SQL:

```sql
-- Criar tabela prompt_configurations se não existir
CREATE TABLE IF NOT EXISTS prompt_configurations (
    id SERIAL PRIMARY KEY,
    prompt_type VARCHAR(50) NOT NULL,
    name VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    user_id INTEGER REFERENCES users(id),
    is_active BOOLEAN DEFAULT true,
    is_default BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER,
    updated_by INTEGER,
    UNIQUE(prompt_type, name)
);

-- Inserir prompts do desenvolvimento para produção
INSERT INTO prompt_configurations (prompt_type, name, content, user_id, is_active, is_default, created_at, updated_at, created_by, updated_by)
VALUES
('GENERAL', 'Template com Código Fonte no Início', 'Você é um especialista em análise de código.

**INSTRUÇÃO CRÍTICA - OBRIGATÓRIO:**
Para cada critério de avaliação, você DEVE incluir EXATAMENTE a tag #FIM_ANALISE_CRITERIO# ao final da análise completa do critério.
Esta tag é ESSENCIAL para garantir que a análise completa seja capturada pelo sistema.

[RESTANTE DO CONTEÚDO DO PROMPT GENERAL...]
#FIM_ANALISE_CRITERIO#

#FIM#', 1, true, false, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 1, 1),

('ARCHITECTURAL', 'architectural_config', 'Analyze the following code from an architectural perspective:

```{language}
{code}
```

Focus on:
1. Design patterns usage
2. Architectural principles compliance
3. Scalability considerations
4. Maintainability aspects
5. System design recommendations', 1, true, false, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 1, 1),

('BUSINESS', 'business_config', 'Analyze the following code focusing on business logic:

```{language}
{code}
```

Evaluate:
1. Business rule implementation
2. Domain-specific patterns
3. Business requirement compliance
4. Process flow efficiency
5. Business value optimization', 1, true, false, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 1, 1)

ON CONFLICT (prompt_type, name) DO UPDATE SET
  content = EXCLUDED.content,
  updated_at = CURRENT_TIMESTAMP;
```

### 2. Configurar Secrets no Streamlit Cloud

**Acesse seu app no Streamlit Cloud**:
1. Vá para: https://share.streamlit.io/
2. Selecione seu workspace
3. Clique no app ou crie um novo
4. Vá para "Settings" → "Secrets"

**Adicione os seguintes secrets**:

```toml
# Configuração PostgreSQL Render
POSTGRES_HOST = "dpg-d4p4s5re5dus7381mdug-a.virginia-postgres.render.com"
POSTGRES_PORT = "5432"
POSTGRES_DB = "verificai"
POSTGRES_USER = "verificai_user"
POSTGRES_PASSWORD = "SUA_SENHA_AQUI"  # Obter do dashboard Render

# Forçar ambiente de produção
ENVIRONMENT = "production"

# API Backend (se necessário)
API_BASE_URL = "http://localhost:8000/api/v1"
```

### 3. Deploy Automático

**Faça push das alterações**:

```bash
git add .
git commit -m "feat: implement production environment detection and prompts sync"
git push origin streamlit-version
```

**O Streamlit Cloud fará deploy automaticamente** após o push!

## 📊 Verificação Pós-Deploy

### 1. Verificar Ambiente de Produção

Acesse seu app no Streamlit Cloud e verifique os logs para confirmar:

```bash
# Logs esperados:
AMBIENTE PRODUCAO DETECTADO - Tentando carregar prompts do PostgreSQL local...
[OK] Prompts carregados do PostgreSQL: ['general', 'architectural', 'business']
```

### 2. Testar Funcionalidades

1. **Login**: Faça login com credenciais de teste
2. **Config Prompts**: Verifique se os prompts carregam corretamente
3. **Upload de Código**: Teste upload e salvamento
4. **Análises**: Verifique se as análises funcionam

## 🛠️ Troubleshooting

### Erro: "Nenhum prompt carregado"

**Causa**: PostgreSQL remoto não configurado ou prompts não sincronizados
**Solução**: Verifique credenciais e execute os inserts SQL

### Erro: "PostgreSQL não disponível"

**Causa**: Credenciais incorretas no secrets
**Solução**: Verifique POSTGRES_HOST, POSTGRES_USER, POSTGRES_PASSWORD

### Erro: "Ambiente detectado como desenvolvimento"

**Causa**: ENVIRONMENT não configurado como "production"
**Solução**: Adicione `ENVIRONMENT = "production"` nos secrets

## 🎯 Features Implementadas

### ✅ Detecção de Ambiente
- Desenvolvimento: PostgreSQL local
- Produção: PostgreSQL remoto (Render)

### ✅ Sistema de Prompts
- Carregamento baseado no ambiente
- Salvar/atualizar prompts
- Fallback para prompts padrão

### ✅ Upload de Código
- Text input direto para PostgreSQL
- File upload via API backend
- Suporte para múltiplos formatos

### ✅ Autenticação
- Login simplificado para desenvolvimento
- Integração com API backend

## 📝 URLs Importantes

- **Streamlit Cloud**: https://share.streamlit.io/
- **Render Dashboard**: https://dashboard.render.com/
- **PostgreSQL Instance**: https://dashboard.render.com/d/dpg-d4p4s5re5dus7381mdug-a
- **Frontend React**: https://avalia-frontend.onrender.com

---

**Status**: Pronto para deploy! Siga os passos acima para colocar em produção.