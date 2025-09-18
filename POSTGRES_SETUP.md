# Configuração PostgreSQL para VerificAI

## Visão Geral

Este documento descreve como configurar o VerificAI para usar PostgreSQL permanentemente, evitando problemas com SQLite na inicialização.

## Configuração Automática

### Método 1: Script de Configuração (Recomendado)

```bash
# Configurar PostgreSQL e iniciar aplicação
python setup-postgres-simple.py
npm run dev

# Ou em um único comando
npm run setup:postgres
npm run dev
```

### Método 2: Script de Inicialização Completo

**Windows:**
```cmd
start-with-postgres.bat
```

**Linux/Mac:**
```bash
./start-with-postgres.sh
```

### Método 3: Usar Docker Compose

```bash
# Iniciar serviços com Docker
docker-compose up -d

# Acessar aplicação
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
```

## Scripts Disponíveis

### `setup-postgres-simple.py`
- Verifica se PostgreSQL está rodando
- Inicia PostgreSQL com Docker se necessário
- Cria banco de dados
- Configura arquivo .env
- Verifica configuração do backend

### `start-with-postgres.bat` (Windows)
- Executa setup-postgres-simple.py
- Instala dependências
- Inicia aplicação

### `start-with-postgres.sh` (Linux/Mac)
- Mesma funcionalidade da versão Windows

## Scripts npm

```bash
# Configurar PostgreSQL e instalar dependências
npm run setup:postgres

# Iniciar com PostgreSQL (configura + inicia)
npm run dev:postgres

# Iniciar aplicação normal (já configurado)
npm run dev
```

## Configurações Importantes

### 1. Forçar PostgreSQL no Backend

O arquivo `backend/app/core/config.py` foi modificado para incluir um validador que força o uso de PostgreSQL:

```python
@field_validator('DATABASE_URL', mode='before')
@classmethod
def validate_database_url(cls, v):
    """Forçar configuração PostgreSQL"""
    if not v:
        return "postgresql://verificai:verificai123@localhost:5432/verificai"

    if v.startswith('sqlite'):
        print("WARNING: SQLite detectado, forçando PostgreSQL")
        return "postgresql://verificai:verificai123@localhost:5432/verificai"

    return v
```

### 2. Proxy do Frontend

O arquivo `frontend/vite.config.ts` foi configurado para usar `localhost:8000`:

```typescript
proxy: {
  '/api': {
    target: 'http://localhost:8000',
    changeOrigin: true,
    secure: false,
  },
}
```

### 3. Variáveis de Ambiente

O arquivo `.env` é configurado automaticamente com:

```env
DATABASE_URL=postgresql://verificai:verificai123@localhost:5432/verificai
REDIS_URL=redis://localhost:6379
# ... outras configurações
```

## Credenciais Padrão

- **Banco de dados:**
  - Host: localhost:5432
  - Database: verificai
  - User: verificai
  - Password: verificai123

- **Aplicação:**
  - Username: admin
  - Password: admin
  - Frontend: http://localhost:3011
  - Backend: http://localhost:8000

## Solução de Problemas

### PostgreSQL não está rodando

1. **Iniciar com Docker:**
   ```bash
   docker run -d --name verificai-postgres -e POSTGRES_DB=verificai -e POSTGRES_USER=verificai -e POSTGRES_PASSWORD=verificai123 -p 5432:5432 postgres:15-alpine
   ```

2. **Instalar PostgreSQL localmente:**
   - Windows: Baixar e instalar PostgreSQL do site oficial
   - Linux: `sudo apt-get install postgresql postgresql-contrib`
   - Mac: `brew install postgresql`

### Erro de conexão com banco de dados

1. Verifique se PostgreSQL está rodando: `netstat -an | grep 5432`
2. Verifique credenciais no arquivo .env
3. Execute o script de configuração: `python setup-postgres-simple.py`

### Frontend não consegue acessar backend

1. Verifique se o proxy está configurado corretamente
2. Certifique-se de que o backend está rodando na porta 8000
3. Verifique o console do navegador por erros de CORS

## Próximos Passos

1. Execute `python setup-postgres-simple.py` para configurar tudo
2. Execute `npm run dev` para iniciar a aplicação
3. Acesse http://localhost:3011 e faça login com admin/admin
4. O sistema agora usará PostgreSQL permanentemente!

## Arquivos Modificados

- `backend/app/core/config.py` - Adicionado validador PostgreSQL
- `frontend/vite.config.ts` - Configurado proxy para localhost:8000
- `package.json` - Adicionados scripts para PostgreSQL
- `.env` - Configurado com PostgreSQL