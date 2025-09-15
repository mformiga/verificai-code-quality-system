# VerificAI Frontend

Frontend do VerificAI Code Quality System - Sistema de análise de código baseado em IA para equipes de QA.

## 🚀 Começando

### Pré-requisitos

- Node.js >= 18.0.0
- npm >= 8.0.0

### Instalação

1. Clone o repositório
2. Instale as dependências:
   ```bash
   npm install
   ```

3. Copie o arquivo de ambiente:
   ```bash
   cp .env.example .env
   ```

4. Inicie o servidor de desenvolvimento:
   ```bash
   npm run dev
   ```

## 📦 Scripts Disponíveis

| Script | Descrição |
|--------|-----------|
| `npm run dev` | Inicia servidor de desenvolvimento |
| `npm run build` | Compila para produção |
| `npm run preview` | Preview da build de produção |
| `npm run test` | Executa testes |
| `npm run test:ui` | Interface de testes interativa |
| `npm run test:coverage` | Relatório de cobertura de testes |
| `npm run lint` | Executa linting |
| `npm run lint:fix` | Corrige problemas de linting |
| `npm run format` | Formata código com Prettier |
| `npm run type-check` | Verificação de tipos TypeScript |

## 🏗️ Arquitetura

### Estrutura do Projeto

```
frontend/
├── src/
│   ├── components/
│   │   ├── common/           # Componentes reutilizáveis
│   │   ├── features/         # Componentes por feature
│   │   └── layout/           # Layout components
│   ├── pages/                # Páginas da aplicação
│   ├── hooks/                # Custom hooks
│   ├── stores/               # State management
│   ├── services/             # API services
│   ├── utils/                # Utilitários
│   ├── types/                # TypeScript types
│   └── assets/               # Assets estáticos
├── tests/                    # Testes
└── public/                   # Arquivos públicos
```

### Tecnologias Utilizadas

- **React 18.3** - UI Framework
- **TypeScript** - Tipagem forte
- **Vite** - Build tool
- **React Router** - Client-side routing
- **Zustand** - State management
- **React Query** - Server state
- **gov.br/ds** - Design System
- **Axios** - HTTP client
- **Vitest** - Testing framework
- **ESLint + Prettier** - Code quality

## 🎨 Design System

Este projeto utiliza o Design System do governo brasileiro (gov.br/ds).

### Cores Principais

- **Primary**: `#1351b4`
- **Secondary**: `#074b99`
- **Success**: `#168821`
- **Warning**: `#f5a623`
- **Danger**: `#d32f2f`

## 🧪 Testes

### Executando Testes

```bash
# Todos os testes
npm test

# Testes em modo watch
npm run test:watch

# Testes com UI interativa
npm run test:ui

# Cobertura de testes
npm run test:coverage
```

### Estrutura de Testes

- **Component Tests**: Testes de componentes React
- **Hook Tests**: Testes de custom hooks
- **Service Tests**: Testes de serviços e API
- **Utility Tests**: Testes de funções utilitárias

## 🚀 Deploy

### Build para Produção

```bash
npm run build
```

O resultado será gerado na pasta `dist/`.

### Variáveis de Ambiente

Variáveis necessárias para produção:

```env
VITE_API_BASE_URL=https://api.verificai.example.com
VITE_WS_BASE_URL=wss://api.verificai.example.com
VITE_APP_VERSION=1.0.0
VITE_ENVIRONMENT=production
```

## 🔧 Configuração

### ESLint

O projeto utiliza ESLint para garantir qualidade de código:

```bash
# Verificar problemas
npm run lint

# Corrigir problemas automaticamente
npm run lint:fix
```

### Prettier

Formatação de código consistente:

```bash
# Formatar código
npm run format

# Verificar formatação
npm run format:check
```

## 📋 Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature: `git checkout -b feature/nova-feature`
3. Faça commit das suas mudanças: `git commit -m 'Add nova feature'`
4. Faça push para a branch: `git push origin feature/nova-feature`
5. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](../../LICENSE) para detalhes.