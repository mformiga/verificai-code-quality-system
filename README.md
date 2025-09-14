# VerificAI Code Quality System

Sistema de análise de código baseado em IA para equipes de QA, projetado para reduzir tempo de análise manual e garantir conformidade com padrões arquiteturais e requisitos de negócio.

## 🎯 Objetivo

O VerificAI é um sistema evolutivo que começa como um assistente de análise de código e se transforma em um guardião autônomo da qualidade, combinando análise estática com compreensão semântica via IA.

## 🚀 Funcionalidades Principais

- **Análise de código-fonte** com critérios configuráveis pelo usuário
- **Verificação de conformidade arquitetural** com upload de documentação
- **Análise de conformidade negocial** comparando código com documentos de negócio
- **Interface web intuitiva** com drag-and-drop e resultados integrados
- **Suporte a múltiplos LLMs** (OpenAI, Anthropic) com estratégias de otimização

## 🏗️ Arquitetura

- **Frontend:** React + TypeScript + Design System do Governo
- **Backend:** Python + FastAPI + LangChain
- **Database:** PostgreSQL + Redis
- **Infrastructure:** Docker + GitHub Actions + Vercel/Cloud Run

## 📁 Estrutura do Projeto

```
verificai-code-quality-system/
├── frontend/          # React UI com TypeScript
├── backend/           # FastAPI backend com Python
├── shared/            # Componentes e tipos compartilhados
├── docs/              # Documentação (PRDs, arquitetura)
├── tests/             # Testes unitários e de integração
└── docker/            # Configurações de container
```

## 🛠️ Tecnologias

### Frontend
- React 18+ com TypeScript
- Redux Toolkit para gerenciamento de estado
- Vite para builds rápidos
- Design System do Governo Brasileiro
- React Markdown para exibição de relatórios

### Backend
- Python 3.11+
- FastAPI para API RESTful
- LangChain para integração com LLMs
- PostgreSQL com SQLAlchemy
- Redis para cache e sessões
- Celery para processamento assíncrono

### DevOps
- Docker & Docker Compose
- GitHub Actions para CI/CD
- Vercel para frontend
- Cloud Run para backend

## 🚀 Getting Started

### Pré-requisitos
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- Contas no OpenAI/Anthropic (para LLMs)

### Setup do Ambiente

1. **Clone o repositório**
   ```bash
   git clone https://github.com/mformiga/verificai-code-quality-system.git
   cd verificai-code-quality-system
   ```

2. **Configure as variáveis de ambiente**
   ```bash
   cp .env.example .env
   # Editar .env com suas chaves de API
   ```

3. **Inicie os serviços com Docker**
   ```bash
   docker-compose up -d
   ```

4. **Acesse a aplicação**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## 📋 Development Workflow

### Branch Strategy
- `main`: Código estável de produção
- `develop`: Integração contínua
- `feature/*`: Desenvolvimento de novas funcionalidades
- `hotfix/*`: Correções emergenciais

### Processo de Contribuição
1. Criar branch a partir de `develop`
2. Desenvolver e testar localmente
3. Criar Pull Request
4. Aguardar code review e CI/CD
5. Merge para `develop`

## 📖 Documentação

- [Product Requirements Document](docs/prd.md)
- [Architecture Documentation](docs/architecture/) (em desenvolvimento)
- [API Documentation](http://localhost:8000/docs)
- [Contributing Guide](CONTRIBUTING.md)

## 🔧 Configuração

### Variáveis de Ambiente
```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/verificai
REDIS_URL=redis://localhost:6379

# LLM Providers
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=sk-your-anthropic-key

# Application
SECRET_KEY=your-secret-key-here
ENVIRONMENT=development
```

## 🧪 Testes

```bash
# Backend tests
cd backend && pytest

# Frontend tests
cd frontend && npm test

# Integration tests
docker-compose exec backend pytest tests/integration/
```

## 📝 Licença

Este projeto está sob licença MIT. Veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🤝 Contribuição

Contribuições são bem-vindas! Por favor leia nosso [Contributing Guide](CONTRIBUTING.md) para detalhes.

## 📞 Contato

- **Repository:** https://github.com/mformiga/verificai-code-quality-system
- **Issues:** https://github.com/mformiga/verificai-code-quality-system/issues

---

**Desenvolvido com ❤️ para equipes de qualidade de software**