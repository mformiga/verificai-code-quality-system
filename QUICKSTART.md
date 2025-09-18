# VerificAI Code Quality System - Quick Start Guide

## 🚀 Início Rápido (Primeira Execução)

### 1. Setup Automático (Recomendado)
```bash
# Instala todas as dependências e configura o ambiente
npm run setup

# Inicia ambos os serviços (frontend + backend)
npm run dev
```

### 2. Setup Manual (Alternativo)
```bash
# Instala dependências
npm run install:all

# Inicia os serviços
npm run dev
```

## 📁 Estrutura do Projeto

```
verificAI-code/
├── backend/                 # FastAPI + Python
│   ├── app/
│   │   ├── main.py         # Entry point
│   │   ├── core/           # Configuração e utilitários
│   │   ├── api/            # Rotas da API
│   │   └── models/         # Modelos de dados
│   ├── (banco de dados PostgreSQL)
│   └── requirements.txt    # Dependências Python
├── frontend/               # React + Vite
│   ├── src/
│   │   ├── pages/          # Páginas da aplicação
│   │   ├── components/     # Componentes React
│   │   ├── hooks/          # Hooks customizados
│   │   └── services/       # Serviços de API
│   └── package.json
└── package.json           # Scripts principais
```

## 🔧 Configuração do Ambiente

### Backend
- **Porta**: 8000
- **Banco de dados**: PostgreSQL (configurado permanentemente)
- **API**: http://localhost:8000/api/v1/
- **Documentação**: http://localhost:8000/api/v1/docs

### Frontend
- **Porta**: Dinâmica (inicia em 3011, encontra primeira disponível)
- **Build**: Vite
- **Hot Reload**: Ativado

## 🛠️ Scripts Úteis

### Desenvolvimento
```bash
npm run dev              # Inicia ambos frontend e backend
npm run dev:frontend     # Inicia apenas o frontend
npm run dev:backend      # Inicia apenas o backend
npm run dev:quick        # Setup + inicia serviços
npm run status           # Mostra URLs dos serviços
```

### Manutenção
```bash
npm run install:all      # Instala todas as dependências
npm run reset:frontend   # Reinstala dependências do frontend
npm run reset:backend    # Limpa cache Python e reinstala
npm run reset:db         # Remove banco de dados (será recriado)
```

### Qualidade de Código
```bash
npm run lint             # Executa linting em ambos os projetos
npm run test             # Executa testes
npm run format           # Formata código com Prettier
```

## 🔑 Acesso à Aplicação

Após executar `npm run dev`:

- **Frontend**: Abra no navegador (verifique o console do terminal para a porta correta)
- **Backend API**: http://localhost:8000/api/v1/
- **API Documentation**: http://localhost:8000/api/v1/docs
- **Login**: Acesse /login no frontend (usuário/senha: admin/admin)

## 🐛 Solução de Problemas Comuns

### Portas em Uso
- **Frontend**: Automaticamente encontra porta disponível (3011+)
- **Backend**: Usa porta 8000 fixa
- Se houver conflito, mude em `backend/app/core/config.py`

### Erros de Importação
- O componente FileUpload foi simplificado para evitar dependências
- Todos os tipos estão definidos inline
- Reinicie o servidor se persistir

### Problemas com Banco de Dados
- Use `python setup-postgres-simple.py` para reconfigurar PostgreSQL
- O banco será recriado automaticamente

### Dependências Ausentes
- Execute `npm run install:all`
- Para problemas específicos: `npm run reset:frontend` ou `npm run reset:backend`

## 📝 Notas de Desenvolvimento

### Funcionalidades Implementadas
- ✅ Sistema de login/logout
- ✅ Upload de arquivos com arrastar e soltar
- ✅ Dashboard principal
- ✅ Navegação entre páginas
- ✅ Banco de dados PostgreSQL
- ✅ API REST com FastAPI

### Configurações Importantes
- Frontend usa proxy Vite para API (`/api` -> `http://localhost:8000`)
- Backend configura CORS para desenvolvimento
- Hot reload ativado em ambos os serviços
- Banco de dados criado automaticamente na inicialização

## 🎯 Próximos Passos

1. **Implementar análise de código** com LLMs
2. **Adicionar mais páginas** ao sistema
3. **Configurar autenticação real** com JWT
4. **Implementar upload real** para backend
5. **Adicionar testes automatizados**

---

**Última atualização**: 2025-09-16
**Versão**: 1.0.0
**Autor**: mformiga