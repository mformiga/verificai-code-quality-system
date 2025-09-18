# VerificAI - Configuração Rápida com Docker

## 🚀 Inicialização Rápida

### Pré-requisitos
- Docker Desktop instalado
- Docker Compose
- Mínimo de 8GB RAM disponível

### 1. Clonar o Repositório
```bash
git clone https://github.com/mformiga/verificai-code-quality-system.git
cd verificai-code-quality-system
```

### 2. Inicialização com Script (Recomendado)
```bash
# Dar permissão de execução ao script (Linux/Mac)
chmod +x quick-start.sh

# Iniciar todos os serviços
./quick-start.sh start
```

### 3. Inicialização Manual
```bash
# Verificar se Docker está rodando
docker info

# Iniciar todos os serviços
docker-compose up -d

# Verificar status dos serviços
docker-compose ps
```

### 4. Acessar a Aplicação
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Database**: localhost:5432

## 📋 Comandos Úteis

### Gerenciamento de Serviços
```bash
# Verificar status
./quick-start.sh status

# Verificar logs
./quick-start.sh logs
./quick-start.sh logs backend
./quick-start.sh logs frontend

# Parar serviços
./quick-start.sh stop

# Reiniciar serviços
./quick-start.sh restart

# Limpar recursos Docker
./quick-start.sh cleanup
```

### Comandos Docker Compose
```bash
# Ver todos os containers
docker-compose ps

# Ver logs em tempo real
docker-compose logs -f [serviço]

# Parar todos os serviços
docker-compose down

# Parar e remover volumes
docker-compose down -v

# Reconstruir imagens
docker-compose build --no-cache

# Escalar serviços
docker-compose up -d --scale backend=2
```

## 🔧 Configuração

### Variáveis de Ambiente
Copie o arquivo `.env.example` para `.env` e ajuste as configurações:

```bash
cp .env.example .env
```

### Configurações Principais
- `DATABASE_URL`: String de conexão com o banco de dados
- `REDIS_URL`: URL do Redis para cache
- `REACT_APP_API_URL`: URL do backend para o frontend
- `SECRET_KEY`: Chave secreta para JWT

## 🏗️ Arquitetura Docker

### Serviços Configurados
1. **PostgreSQL**: Banco de dados principal
2. **Redis**: Cache e sessões
3. **Backend**: API FastAPI com auto-reload
4. **Frontend**: React com Vite e hot-reload
5. **Celery Worker**: Processamento de tarefas assíncronas
6. **Celery Beat**: Agendador de tarefas

### Portas Utilizadas
| Serviço | Porta Host | Porta Container |
|---------|------------|-----------------|
| Frontend | 3000 | 3011 |
| Backend API | 8000 | 8000 |
| Database | 5432 | 5432 |
| Redis | 6379 | 6379 |

### Volumes Persistidos
- `postgres_data`: Dados do PostgreSQL
- `backend-cache`: Cache de build do backend

## 🐛 Problemas Comuns

### Docker não está rodando
```bash
# Verificar status do Docker
docker info

# Iniciar Docker Desktop (Windows/macOS)
# Ou verificar se o serviço está rodando (Linux)
sudo systemctl start docker
```

### Portas já estão em uso
```bash
# Verificar processos usando as portas
netstat -tulpn | grep :3000
netstat -tulpn | grep :8000

# Matar processos se necessário
sudo kill -9 <PID>
```

### Problemas de permissão
```bash
# Adicionar usuário ao grupo docker (Linux)
sudo usermod -aG docker $USER

# Fazer logout e login novamente
```

### Build falhando
```bash
# Limpar cache do Docker
docker system prune -a

# Reconstruir do zero
docker-compose build --no-cache
```

## 📊 Monitoramento

### Health Checks
```bash
# Verificar saúde dos serviços
curl http://localhost:8000/health
curl http://localhost:3000

# Verificar status dos containers
docker-compose ps
```

### Logs
```bash
# Logs do backend
docker-compose logs -f backend

# Logs do frontend
docker-compose logs -f frontend

# Logs do banco de dados
docker-compose logs -f postgres
```

## 🔄 Desenvolvimento

### Hot Reload
O ambiente está configurado para desenvolvimento com hot reload:
- Backend: Alterações nos arquivos Python recarregam automaticamente
- Frontend: Alterações nos arquivos React atualizam o navegador

### Acessar containers
```bash
# Acessar container do backend
docker-compose exec backend bash

# Acessar container do frontend
docker-compose exec frontend bash

# Acessar banco de dados
docker-compose exec postgres psql -U verificai -d verificai
```

## 🧪 Testes

### Rodar testes
```bash
# Testes do backend
docker-compose run --rm backend pytest

# Testes do frontend
docker-compose run --rm frontend npm test

# Testes de integração
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

## 🚀 Deploy

### Build para Produção
```bash
# Construir imagens otimizadas
docker-compose -f docker-compose.prod.yml build

# Subir para produção
docker-compose -f docker-compose.prod.yml up -d
```

### Variáveis de Produção
- `ENVIRONMENT=production`
- `DEBUG=false`
- `LOG_LEVEL=INFO`
- Configurar CORS e segurança apropriados

## 📝 Notas

1. **Performance**: O ambiente está otimizado para desenvolvimento com cache e volumes
2. **Segurança**: Para produção, ajuste variáveis de ambiente e configure HTTPS
3. **Recursos**: Certifique-se de ter RAM suficiente para todos os serviços
4. **Backup**: Dados importantes estão persistidos em volumes Docker

## 🆘 Suporte

Se encontrar problemas:
1. Verifique os logs: `docker-compose logs`
2. Confirme se Docker está rodando: `docker info`
3. Verifique portas disponíveis: `netstat -tulpn`
4. Limpe e reconstrua: `docker-compose down && docker-compose build --no-cache`