# Guia de Deploy na Vercel com Supabase

Este guia explica como configurar o deploy do VerificAI na Vercel usando Supabase como banco de dados.

## 📋 Pré-requisitos

1. **Conta Vercel**: [vercel.com](https://vercel.com)
2. **Projeto Supabase**: [supabase.com](https://supabase.com)
3. **Repositório GitHub** com o código do VerificAI

## 🔧 Configuração do Supabase

### 1. Criar Projeto Supabase
1. Acesse [supabase.com](https://supabase.com)
2. Clique em "Start your project"
3. Faça login com GitHub
4. Crie novo projeto:
   - **Organization**: Sua organização
   - **Project Name**: verificai-production
   - **Database Password**: Crie uma senha forte
   - **Region**: Escolha a região mais próxima dos seus usuários

### 2. Obter Credenciais
No dashboard do Supabase, vá em **Settings > API**:

Copie as seguintes informações:
```
Project URL: https://jjxmfidggofuaxcdtkrd.supabase.co
Project Ref: jjxmfidggofuaxcdtkrd
API Key (anon): eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
API Key (service_role): eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Importante**: A service_role key só deve ser usada no backend!

### 3. Configurar Database Schema
O sistema criará as tabelas automaticamente, mas você pode pré-criar:

```sql
-- Crie extensões necessárias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- O sistema criará as tabelas automaticamente via SQLAlchemy
```

## 🚀 Configuração da Vercel

### 1. Importar Projeto
1. Acesse [vercel.com](https://vercel.com)
2. Clique em "Add New..." → "Project"
3. Importe seu repositório GitHub
4. Configure o framework: **Other**
5. Configure as configurações:

**Build Command:**
```bash
cd backend && pip install -r requirements.txt
```

**Output Directory:**
```bash
backend
```

**Install Command:**
```bash
cd backend && pip install -r requirements.txt
```

### 2. Environment Variables
Na Vercel, vá em **Settings → Environment Variables** e adicione:

```bash
# Environment Detection
VERCEL=true

# Supabase Configuration
SUPABASE_URL=https://jjxmfidggofuaxcdtkrd.supabase.co
SUPABASE_PROJECT_REF=jjxmfidggofuaxcdtkrd
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...  # Cole aqui sua anon key
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...  # Cole aqui sua service role key

# Database (será configurado automaticamente)
# DATABASE_URL não precisa ser definida, será gerada pela aplicação

# Security
SECRET_KEY=sua-chave-secreta-muito-forte-aqui
JWT_SECRET_KEY=sua-chave-jwt-secreta-aqui
JWT_ALGORITHM=HS256

# API Keys
OPENAI_API_KEY=sua-chave-openai
ANTHROPIC_API_KEY=sua-chave-anthropic

# Application
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# CORS
BACKEND_CORS_ORIGINS=https://seu-dominio.vercel.app,https://seu-dominio-custom.com

# Rate Limiting
RATE_LIMIT_REQUESTS_PER_MINUTE=60
RATE_LIMIT_BURST=10
```

### 3. Configurar Serverless Function
Crie o arquivo `api/index.js` na raiz do projeto:

```javascript
// api/index.js
const { exec } = require('child_process');

module.exports = async (req, res) => {
  // Handle CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  // Proxy para o backend Python
  exec(`cd backend && python -c "
import os
os.environ['REQUEST_METHOD'] = '${req.method}'
os.environ['PATH_INFO'] = '${req.url}'
from app.main import app
import uvicorn
uvicorn.run(app, host='0.0.0.0', port=8000)
"`, (error, stdout, stderr) => {
    if (error) {
      console.error('Error:', error);
      return res.status(500).json({ error: 'Internal Server Error' });
    }

    try {
      const response = JSON.parse(stdout);
      res.status(200).json(response);
    } catch (e) {
      res.status(200).send(stdout);
    }
  });
};
```

### 4. Vercel Configuration
Crie o arquivo `vercel.json` na raiz:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.js",
      "use": "@vercel/node"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "/api/index.js"
    }
  ],
  "env": {
    "PYTHON_VERSION": "3.11"
  }
}
```

## 🧪 Testar Deploy

### 1. Deploy Inicial
1. Commit todas as mudanças no GitHub
2. Na Vercel, clique em "Deploy"
3. Aguarde o build e deploy

### 2. Testar API
```bash
# Testar health check
curl https://seu-dominio.vercel.app/api/v1/health

# Testar ambiente
curl https://seu-dominio.vercel.app/api/v1/debug/env
```

### 3. Verificar Logs
Na Vercel, vá em **Functions → Logs** para verificar:
- Database connection logs
- Environment detection
- Error messages

## 🔍 Troubleshooting

### Erro: "Database connection failed"
1. Verifique as environment variables na Vercel
2. Confirme se a SUPABASE_SERVICE_ROLE_KEY está correta
3. Verifique se o projeto Supabase está ativo

### Erro: "Module not found"
1. Verifique requirements.txt
2. Confirme Python version na Vercel
3. Verifique se todas as dependências estão listadas

### Performance Issues
1. Configure database pool size para serverless:
   ```python
   # No config.py
   if IS_VERCEL:
       DATABASE_POOL_SIZE = 5
       DATABASE_MAX_OVERFLOW = 0
   ```

## 📊 Monitoramento

### Vercel Analytics
- Ative na aba Analytics
- Monitore performance e erros

### Supabase Monitoring
- Dashboard do Supabase
- Database usage metrics
- Connection logs

### Logs Customizados
```python
# Adicione logging específico
import logger

logger.info(f"Database type: {DATABASE_TYPE}")
logger.info(f"Environment: production")
logger.info("Deployment successful")
```

## 🔒 Security

### Important Security Notes

1. **NUNCA** exponha a service_role key no frontend
2. **SEMPRE** use HTTPS em produção
3. **Configure** Row Level Security (RLS) no Supabase
4. **ROTE** as secrets via environment variables

### Row Level Security (RLS)
No Supabase, configure RLS para cada tabela:

```sql
-- Exemplo para tabela users
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Política para usuários verem apenas seus dados
CREATE POLICY "Users can view own data" ON users
FOR SELECT USING (auth.uid()::text = id::text);
```

## 🚀 Pós-Deploy

### 1. Configurar Custom Domain
1. Na Vercel: Settings → Domains
2. Adicione seu domínio
3. Configure DNS records

### 2. Backup Strategy
1. Configure backups automáticos no Supabase
2. Exporte dados regularmente

### 3. CI/CD Pipeline
Configure GitHub Actions para automatizar deploys:

```yaml
# .github/workflows/deploy.yml
name: Deploy to Vercel

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v20
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.ORG_ID }}
          vercel-project-id: ${{ secrets.PROJECT_ID }}
```

## 📝 Checklist Final

- [ ] Projeto Supabase criado e ativo
- [ ] Environment variables configuradas na Vercel
- [ ] Keys copiadas corretamente
- [ ] Build configurado
- [ ] CORS origins configuradas
- [ ] Deploy testado e funcionando
- [ ] Logs monitorados
- [ ] Segurança revisada
- [ ] Backup configurado
- [ ] Custom domain configurado

---

**Suporte**: Se encontrar problemas, verifique os logs na Vercel e no dashboard do Supabase para detalhes específicos do erro.