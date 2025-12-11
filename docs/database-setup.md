# Configuração de Banco de Dados - PostgreSQL Local e Supabase (Vercel)

Este documento descreve como o sistema foi configurado para usar PostgreSQL localmente e Supabase em deploy na Vercel.

## 🏗️ Arquitetura

O sistema detecta automaticamente o ambiente e configura o banco de dados apropriado:

- **Desenvolvimento Local**: PostgreSQL localhost
- **Produção (Vercel)**: Supabase PostgreSQL

## 📁 Arquivos Modificados

### 1. Backend Configuration
- `backend/app/core/config.py`: Configuração principal com detecção de ambiente
- `backend/app/core/database.py`: Conexão e configurações específicas por ambiente

### 2. Environment Variables
- `.env`: Configuração local
- `.env.example`: Template de configuração
- `.env.vercel`: Configuração para deploy na Vercel

### 3. Testes
- `backend/test_database_config.py`: Script para testar configurações

## 🔧 Configuração Local

### PostgreSQL Local
1. Instale PostgreSQL 15+
2. Crie o banco de dados:
   ```sql
   CREATE DATABASE verificai;
   CREATE USER verificai WITH PASSWORD 'verificai123';
   GRANT ALL PRIVILEGES ON DATABASE verificai TO verificai;
   ```

### Environment Variables
```bash
# .env
VERCEL=false
DATABASE_URL=postgresql://verificai:verificai123@localhost:5432/verificai
```

### Testar Configuração Local
```bash
cd backend
python test_database_config.py
```

## 🚀 Configuração Produção (Vercel)

### Supabase Setup
1. Crie um projeto em [supabase.com](https://supabase.com)
2. Vá para Settings > API
3. Copie as seguintes informações:
   - Project URL
   - anon public key
   - service_role key (NUNCA exponha publicamente)

### Vercel Environment Variables
Configure estas variáveis no dashboard da Vercel:

```bash
VERCEL=true
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_PROJECT_REF=your-project-ref
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

### Security Notes
- `SUPABASE_SERVICE_ROLE_KEY`: Use apenas no backend, nunca no frontend
- `SUPABASE_ANON_KEY`: Pode ser usado no frontend
- Configure Row Level Security (RLS) no Supabase

## 🔄 Como Funciona

### Environment Detection
```python
# Em config.py
is_vercel = os.getenv('VERCEL', 'false').lower() == 'true'

if is_vercel:
    # Usa Supabase
    db_url = f"postgresql://postgres.{project_ref}:{service_role_key}@aws-0-us-east-1.pooler.supabase.com:6543/postgres"
else:
    # Usa PostgreSQL local
    db_url = "postgresql://verificai:verificai123@localhost:5432/verificai"
```

### Database Configuration
```python
# Em database.py
if IS_VERCEL:
    # Configurações otimizadas para serverless
    config = {
        "pool_size": 5,
        "max_overflow": 0,
        "pool_timeout": 10,
        "connect_args": {"sslmode": "require"}
    }
else:
    # Configurações para servidor local
    config = {
        "poolclass": QueuePool,
        "pool_size": 20,
        "max_overflow": 10
    }
```

## 🛠️ Troubleshooting

### Problemas Locais
1. **PostgreSQL não inicia**:
   - Verifique se o serviço está rodando
   - Windows: `services.msc` → PostgreSQL
   - Linux/Mac: `brew services start postgresql` ou `sudo systemctl start postgresql`

2. **Connection refused**:
   - Verifique se PostgreSQL está na porta 5432
   - Confirme credenciais no .env

### Problemas na Vercel
1. **Supabase connection failed**:
   - Verifique environment variables na Vercel
   - Confirme se Supabase project está ativo
   - Check IP allowlist no Supabase

2. **Service role key error**:
   - Nunca commit service_role keys
   - Use environment variables na Vercel

### Testes
```bash
# Testar configuração atual
python backend/test_database_config.py

# Forçar ambiente local
export VERCEL=false
python backend/test_database_config.py

# Simular ambiente Vercel
export VERCEL=true
export SUPABASE_SERVICE_ROLE_KEY=your-key
python backend/test_database_config.py
```

## 📊 Monitoramento

### Logs
O sistema inclui logging específico por ambiente:
- Local: "PostgreSQL connection failed"
- Vercel: "Supabase connection failed"

### Health Checks
Endpoint `/health` verifica conectividade do banco de dados:
```bash
curl http://localhost:8000/api/v1/health
```

## 🔄 Migrations

### Local
```bash
# Se usando Alembic
alembic upgrade head

# Se precisa criar tabelas manualmente
python -c "from app.core.database import create_tables; create_tables()"
```

### Supabase
1. Use Supabase Dashboard para criar tabelas
2. Ou configure migrations do projeto local
3. Aplique no Supabase via SQL ou migrations

## 📝 Próximos Passos

1. **Redis**: Considerar Redis Cloud para produção
2. **Backups**: Configurar backups automáticos no Supabase
3. **Monitoring**: Integrar monitoring específico para database
4. **Performance**: Otimizar queries para ambiente serverless

## 🆘 Suporte

Se encontrar problemas:

1. Verifique os logs específicos do ambiente
2. Execute o script de teste
3. Confirme environment variables
4. Verifique configurações de firewall/rede

---

**Importante**: Nunca commit keys ou credenciais reais no repositório! Use sempre environment variables.