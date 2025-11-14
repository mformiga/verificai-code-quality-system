# VerificAI Code Quality System - Product Requirements Document (PRD)

*Documento em construção - Modo Interativo*

---

## Goals and Background Context

### Goals
- Sistema de análise de código baseado em IA com critérios configuráveis pelo usuário
- Verificação de conformidade arquitetural com upload de documentação
- Análise de conformidade negocial comparando código com documentos de negócio
- Interface web para upload de código, configuração de prompts e geração de relatórios
- Redução de 40% no tempo de análise manual para equipes de QA

### Background Context
O VerificAI é um sistema evolutivo que começa como um assistente de análise de código e se transforma em um guardião autônomo da qualidade. Atualmente, equipes de QA gastam tempo excessivo em análises manuais de código-fonte, enfrentando dificuldades em garantir conformidade com padrões arquiteturais e requisitos de negócio. A solução combina análise estática com compreensão semântica via IA, permitindo personalização de critérios e integração com documentação existente, evoluindo de um MVP focado para um sistema completo de monitoramento contínuo.

### Change Log
| Data | Versão | Descrição | Autor |
|------|--------|-----------|-------|
| 2025-09-13 | v1.0 | Criação inicial do PRD baseado no Project Brief | John (PM) |

---

## Requirements

### Functional Requirements

**FR1:** O sistema deve permitir upload de pastas de código-fonte com inclusão automática de subpastas e arquivos
**FR2:** O sistema deve fornecer interface para configuração de três prompts editáveis: critérios gerais, conformidade arquitetural e conformidade negocial  
**FR3:** O sistema deve aceitar upload de documentos de arquitetura para **verificação por IA** de conformidade com código implementado
**FR4:** O sistema deve aceitar upload de documentos de negócio (histórias, épicos, regras) para **análise por IA** semântica de conformidade
**FR5:** O sistema deve **gerar por IA** relatórios estruturados em Markdown com descrição de problemas, exemplos de código incorreto e localização exata
**FR6:** O sistema deve permitir configuração de regras de exclusão para ignorar pastas/arquivos específicos (node_modules, testes, etc.)
**FR7:** O sistema deve permitir download dos relatórios gerados para arquivo local
**FR8:** O sistema deve suportar análise de múltiplas linguagens de programação com prioridade para JavaScript, Python e TypeScript
**FR9:** O sistema deve processar projetos de até 10MB no MVP com limite de processamento de 200 arquivos em < 10 minutos
**FR10:** O sistema deve fornecer área administrativa separada para gerenciamento de prompts e configurações
**FR11:** O sistema deve fornecer **modo manual alternativo** que permita ao usuário inserir manualmente resultados de análise para todas as categorias (arquitetura, critérios gerais e negocial) quando APIs de IA estiverem indisponíveis

### Non-Functional Requirements

**NFR1:** O sistema deve não armazenar permanentemente código-fonte (processamento temporário apenas)
**NFR2:** O sistema deve implementar segurança com HTTPS, sanitização de inputs e rate limiting
**NFR3:** O sistema deve ter interface responsiva para tablets (não smartphones no MVP)
**NFR4:** O sistema deve suportar últimas 2 versões dos principais navegadores (Chrome, Firefox, Safari, Edge)
**NFR5:** O sistema deve implementar logging estruturado para monitoramento e debugging

---

## User Interface Design Goals

### Overall UX Vision
Interface minimalista e focada em produtividade que prioriza a eficiência de equipes de QA. O design deve reduzir fricção no fluxo de trabalho de análise, com navegação intuitiva entre upload, configuração e visualização de resultados. A experiência deve transmitir confiança e profissionalismo, adequada para ambientes corporativos de desenvolvimento de software.

### Key Interaction Paradigms
- **Drag-and-Drop** para upload de pastas e documentos
- **Wizard Step-by-Step** para configuração inicial de prompts
- **Tab-based Navigation** entre diferentes tipos de análise
- **Real-time Preview** para visualização imediata de resultados
- **Inline Editing** para ajustes rápidos de configurações
- **Progressive Disclosure** para recursos avançados sem sobrecarregar interface principal

### Core Screens and Views
1. **Tela Principal/Upload** - Área central para drag-and-drop de pastas de código
2. **Tela de Edição de Prompts** - Interface para edição dos três prompts (critérios gerais, arquitetural, negocial) com syntax highlighting e salvamento automático
3. **Tela de Critérios Gerais** - Interface para manter critérios de avaliação com resultados de análise e relatório integrados, incluindo opção para edição manual quando APIs indisponíveis
4. **Tela de Upload de Documento de Arquitetura** - Área dedicada para upload de documento de arquitetura com resultado da análise de conformidade em relação ao código fonte avaliado com relatório integrado, incluindo opção para edição manual quando APIs indisponíveis
5. **Tela de Upload de Documento de Negócio** - Área dedicada para upload de documentos de negócio com resultado da análise semântica em relação ao código font avaliado com srelatório integrado, incluindo opção para edição manual quando APIs indisponíveis

### Branding
Utilizar o padrão digital de governo denominado Design System publicado em https://www.gov.br/ds/home, incorporando paleta de cores, tipografia e componentes visuais consistentes com padrões governamentais brasileiros.

### Target Device and Platforms: Web Responsive
Interface responsiva compatível com desktop e tablets, otimizada para as últimas 2 versões dos principais navegadores (Chrome, Firefox, Safari, Edge). Não há suporte para smartphones no MVP.

---

## Technical Assumptions

### Repository Structure: Monorepo
O sistema utilizará uma estrutura de repositório monorepo para organizar código frontend, backend e componentes compartilhados. Esta abordagem facilita o desenvolvimento integrado, versionamento consistente e compartilhamento de tipos e utilitários entre frontend e backend.

### Service Architecture: Monolith
O sistema será implementado como uma aplicação monolítica para o MVP, com backend Python/FastAPI servindo tanto a API REST quanto a interface web. Esta decisão simplifica o deployment, reduz complexidade operacional e permite entrega mais rápida do MVP. A arquitetura deve ser projetada para evolução futura para microserviços.

### Testing Requirements: Unit + Integration
O sistema implementará testes unitários para componentes individuais e testes de integração para fluxos críticos entre frontend e backend. Testes end-to-end serão limitados a fluxos principais de usuário para otimizar tempo de desenvolvimento do MVP.

### Additional Technical Assumptions and Requests

**Frontend:**
- **Framework:** React com TypeScript para melhor desenvolvimento e maintainability
- **UI Components:** Design System do governo brasileiro (gov.br/ds)
- **State Management:** Redux Toolkit para gerenciamento de estado complexo
- **File Upload:** Implementação customizada com drag-and-drop
- **Markdown Rendering:** React Markdown para exibição de relatórios
- **Build Tool:** Vite para builds rápidos e otimizados

**Backend:**
- **Language:** Python 3.11+ para excelente suporte a IA e bibliotecas científicas
- **Framework:** FastAPI para API RESTful de alta performance
- **LLM Integration:** LangChain para gerenciamento de prompts e chains
- **File Processing:** Bibliotecas específicas por linguagem (ast para Python, etc.)
- **Task Queue:** Celery com Redis para processamento assíncrono de análises longas

**Database:**
- **Primary:** PostgreSQL para dados relacionais e configurações
- **Cache:** Redis para sessões e cache de resultados
- **File Storage:** Sistema de arquivos local para MVP (evolução para S3 em produção)

**Hosting/Infrastructure:**
- **MVP:** Docker containers com docker-compose para desenvolvimento local
- **Production:** Vercel para frontend, Cloud Run para backend (evolução para cloud provider completo)
- **Environment:** Variáveis de ambiente para configuração de APIs e segredos
- **Monitoring:** Logs estruturados e métricas básicas

**Security:**
- **Authentication:** API keys para acesso ao sistema (MVP)
- **Data Privacy:** Não armazenar código-fonte permanentemente
- **Rate Limiting:** Limitação de requisições para prevenir abusos

### GitHub Integration & Repository Management

**Repository Setup:**
- **Primary Repository:** https://github.com/mformiga/verificai-code-quality-system
- **Repository Type:** Public repository com documentação e código-fonte abertos
- **Branch Strategy:** 
  - `main`: Branch principal com código estável e pronto para produção
  - `develop`: Branch de desenvolvimento com integração contínua
  - `feature/*`: Branches para desenvolvimento de novas funcionalidades
  - `hotfix/*`: Branches para correções emergenciais

**Development Workflow:**
- **Local Development:** Clone do repositório para desenvolvimento local com Docker
- **Pull Request Process:** PRs requerem aprovação e passagem em testes automáticos
- **CI/CD Pipeline:** GitHub Actions para build, test e deploy automatizados
- **Code Review:** Processo de revisão por pares para todo código mergeado

**GitHub Configuration:**
- **Repository Settings:** Configuração de branches protegidos (main, develop)
- **Automated Security:** Dependabot para atualização automática de dependências
- **Issue Management:** Templates para bugs, features e melhorias
- **Project Management:** GitHub Projects para rastreamento de sprints e roadmap

**Documentation Strategy:**
- **README.md:** Documentação principal do projeto com setup e instruções
- **CONTRIBUTING.md:** Guia para contribuidores com padrões de código e workflow
- **docs/:** Diretório com documentação detalhada, PRDs e arquitetura
- **GitHub Wiki:** Documentação colaborativa e guias de uso

**Environment Management:**
- **Development:** Ambiente local com docker-compose
- **Staging:** Ambiente de staging vinculado ao branch develop
- **Production:** Ambiente de produção com deploy automático do branch main
- **Secrets Management:** GitHub Secrets para armazenamento seguro de chaves de API

### LLM Integration Details

**LangChain Configuration:**
- **Prompt Management:** Templates estruturados para cada tipo de análise (geral, arquitetural, negocial)
- **Chain Orchestration:** Sequências de prompts para análise multi-etapas
- **Memory Management:** Context window handling para projetos grandes
- **Token Optimization:** Estratégias para minimizar custos de LLM

**Prompt Engineering Strategy:**
- **Output Formatting:** Structured output em markdown para parsing consistente de resultados

### Token Optimization Strategies

**Pre-processing Optimization:**
- **Code Minification:** Remoção de comentários e whitespace não essenciais antes do envio ao LLM
- **Selective File Analysis:** Algoritmos inteligentes para identificar arquivos mais relevantes para cada tipo de análise
- **Duplicate Detection:** Identificação e remoção de código duplicado para evitar processamento redundante

**Context Management:**
- **Sliding Window Technique:** Janelas deslizantes para análise contínua de arquivos grandes
- **Hierarchical Analysis:** Análise em múltiplos níveis (arquivo → classe → função) com agregação de resultados
- **Progressive Disclosure:** Revelação gradual de contexto baseada na necessidade da análise atual
- **Context Compression:** Técnicas de compressão semântica para maximizar informação dentro do limite de tokens

**Cost Control Mechanisms:**
- **Token Budgeting:** Alocação dinâmica de tokens por tipo de análise com base na importância relativa
- **Adaptive Sampling:** Redução proporcional do contexto quando projetos excedem limites de token
- **Batch Processing:** Agrupamento inteligente de análises similares para aproveitar contexto compartilhado
- **Cache Strategy:** Cache de resultados para análises repetidas do mesmo código
- **Smart Retry:** Retentativas estratégicas apenas para análises de alto valor quando custos excedem limites

**Advanced Techniques:**
- **Embedding-based Pre-filtering:** Uso de embeddings para pré-selecionar trechos de código mais relevantes
- **Semantic Deduplication:** Identificação de código semanticamente equivalente para evitar processamento duplicado

---

## Epic List

### Proposta de Epics para o MVP do VerificAI:

**Epic 1: Foundation & Core Infrastructure - Estabelecimento da base técnica e configuração inicial do sistema, incluindo setup do repositório GitHub, configuração do monorepo e implementação dos serviços fundamentais.**

**Epic 2: Core File Processing & Upload System - Implementação do sistema de upload e processamento de arquivos, incluindo interface drag-and-drop, análise de estruturas de pastas e configuração de regras de exclusão.**

**Epic 3: Prompt Management & Configuration System - Desenvolvimento do sistema de gerenciamento de prompts, incluindo interface para edição dos três tipos de prompts (geral, arquitetural, negocial) com syntax highlighting e persistência.**

**Epic 4: LLM Integration & Analysis Engine - Integração com múltiplos provedores de LLM usando LangChain, implementação das estratégias de otimização de tokens e desenvolvimento do motor de análise principal.**

**Epic 5: Document Upload & Analysis Interfaces - Implementação das três telas de análise com upload integrado: tela de critérios gerais (configuração + resultados), tela de documento de arquitetura (upload + análise + resultados) e tela de documento de negócio (upload + análise semântica + resultados).**

---

## Epic Details

### Epic 1: Foundation & Core Infrastructure

**Epic Goal:** Estabelecer a base técnica completa do projeto, incluindo repositório GitHub configurado, estrutura de monorepo, serviços fundamentais (backend FastAPI, frontend React, banco de dados) e pipeline de CI/CD inicial.

---

**Story 1.1: Repository Setup & Initial Structure**  
Como um desenvolvedor,  
Quero criar e configurar o repositório GitHub inicial com estrutura de monorepo,  
Para que tenhamos uma base sólida e organizada para desenvolvimento colaborativo.

**Acceptance Criteria:**
1. Repositório GitHub público criado com nome `verificai-code-quality-system`
2. Estrutura de monorepo implementada com diretórios: `frontend/`, `backend/`, `shared/`, `docs/`, `tests/`
3. Arquivos de configuração inicial: `README.md`, `.gitignore`, `docker-compose.yml`, `package.json` (root)
4. Branches principais configurados: `main` e `develop` com proteção no branch `main`
5. GitHub Actions workflow básico configurado para linting e testes
6. Documentação inicial de setup de ambiente de desenvolvimento

**Story 1.2: Backend Service Foundation**  
Como um arquiteto de sistemas,  
Quero configurar o serviço backend FastAPI com estrutura modular e conexão com banco de dados,  
Para que tenhamos uma API robusta para processamento de análises.

**Acceptance Criteria:**
1. FastAPI backend configurado com Python 3.11+ e estrutura modular (routers, models, services)
2. PostgreSQL database configurada com models iniciais para usuários, configurações e análises
3. Redis configurado para cache e sessões
4. Sistema de configuração com environment variables e secrets management
5. API endpoints básicos: health check, configuração de prompts, gerenciamento de usuários
6. Logging estruturado implementado com níveis apropriados
7. Documentação da API gerada automaticamente com Swagger/OpenAPI

**Story 1.3: Frontend Application Structure**  
Como um desenvolvedor frontend,  
Quero configurar a aplicação React com TypeScript e integração com o backend,  
Para que tenhamos uma base sólida para construir a interface do usuário.

**Acceptance Criteria:**
1. React application configurada com TypeScript e Vite
2. Design System do governo brasileiro (gov.br/ds) integrado
3. Redux Toolkit configurado para gerenciamento de estado
4. Rotas principais definidas para as 5 telas do sistema
5. Integração com API backend implementada com client HTTP
6. Sistema de autenticação básico com API keys
7. Interface responsiva implementada para desktop e tablets

**Story 1.4: Development Environment & CI/CD Pipeline**  
Como um engenheiro de DevOps,  
Quero configurar ambiente de desenvolvimento local com Docker e pipeline de CI/CD completo,  
Para que tenhamos desenvolvimento consistente e deploy automatizado.

**Acceptance Criteria:**
1. Docker containers configurados para frontend, backend e banco de dados
2. Docker Compose configurado para desenvolvimento local com todos os serviços
3. GitHub Actions pipeline configurado com stages: build, test, security scan, deploy
4. Deploy automático configurado para Vercel (frontend) e Cloud Run (backend)
5. Secrets management configurado no GitHub para chaves de API e credenciais
6. Monitoring básico implementado com logs e métricas
7. Processo de deploy manual para staging e automático para produção

---

### Epic 2: Core File Processing & Upload System

**Epic Goal:** Implementar o sistema completo de upload e processamento de arquivos de código-fonte, incluindo interface drag-and-drop, análise de estruturas de pastas e preparação dos arquivos para análise.

---

**Story 2.1: File Upload Interface & Drag-and-Drop**  
Como um usuário de QA,  
Quero fazer upload de pastas de código através de interface intuitiva com drag-and-drop,  
Para que possa facilmente selecionar e enviar os arquivos para análise.

**Acceptance Criteria:**
1. Interface drag-and-drop implementada na tela principal com área claramente demarcada
2. Suporte para upload de pastas completas com inclusão automática de subpastas e arquivos
3. Visualização em tempo real do progresso de upload com indicadores de status
4. Interface alternativa de click-to-upload para usuários que preferem navegação tradicional
5. Feedback visual claro para upload concluído com sucesso ou erros
6. Lista de arquivos enviados com informações básicas (Path da pasta e o nome do arquivo)

---

### Epic 3: Prompt Management & Configuration System

**Epic Goal:** Desenvolver o sistema básico de gerenciamento de prompts, incluindo interface dedicada para edição dos três tipos de prompts com syntax highlighting e salvamento de versão anterior.

---

**Story 3.1: Prompt Configuration Interface**  
Como um usuário de QA,  
Quero acessar uma tela dedicada para configurar e editar os três tipos de prompts de análise,  
Para que possa personalizar como o sistema avaliará o código-fonte.

**Acceptance Criteria:**
1. Tela dedicada de edição de prompts implementada com layout claro e organizado
2. Três seções distintas para cada tipo de prompt: Critérios Gerais, Conformidade Arquitetural, Conformidade Negocial
3. Editor de texto com syntax highlighting para melhor legibilidade dos prompts
4. Sistema de autosalvamento automático a cada 30 segundos
5. Botões manuais para salvar, descartar alterações e restaurar padrões
6. Indicadores visuais de status (salvo, não salvo, erro)
7. Sistema para salvar uma versão anterior do prompt antes de cada alteração

---

### Epic 4: LLM Integration & Analysis Engine

**Epic Goal:** Implementar o motor essencial de análise que coordena o processo completo de integração com LLM e processamento de código-fonte.

---

**Story 4.1: Analysis Engine Core**  
Como um desenvolvedor backend,  
Quero implementar o motor principal de análise que coordena todo o processo,  
Para que o sistema possa executar análises completas de forma eficiente e confiável.

**Acceptance Criteria:**
1. Orquestrador de análise implementado com gerenciamento de fluxo completo
2. Sistema de fila para processamento assíncrono de análises longas
3. Integração básica com provedores de LLM (OpenAI, Anthropic)
4. Sistema de retry e recuperação para falhas de LLM
5. Sistema de agregação de resultados de análises individuais
6. Interface para monitoramento do progresso de análise em tempo real
7. Sistema de cancelamento e limpeza para análises interrompidas
8. Sistema de otimização básica de tokens (minificação e chunking simples)
9. O sistema permite apenas uma análise por vez (critérios gerais ou arquitetura ou regras de negócio)

---

### Epic 5: Document Upload & Analysis Interfaces

**Epic Goal:** Implementar as três telas principais de análise com upload integrado, onde cada tela combina configuração, upload de documentos, execução de análise e exibição de resultados de forma coesa.

---

**Story 5.1: General Criteria Analysis Interface**  
Como um usuário de QA,  
Quero acessar uma tela dedicada para configurar critérios gerais de avaliação e ver os resultados da análise por IA,  
Para que possa avaliar o código-fonte baseado em padrões de qualidade gerais definidos por mim.

**Acceptance Criteria:**
1. Tela dedicada implementada com área para configuração de critérios gerais
2. Botão para iniciar análise usando o prompt configurado de critérios gerais
4. Interface de progresso mostrando status da análise em tempo real
5. Exibição dos resultados da análise de critérios gerais formatados em Markdown
6. Opção para edição manual dos resultados quando APIs de IA estiverem indisponíveis
7. Botão para download do relatório de análise em formato Markdown
8. Sistema mostrando apenas a última análise realizada na tela
9. Sistema apresenta o resultado da análise ao lado de cada critério definido pelo QA

**Story 5.2: Architecture Document Analysis Interface**  
Como um usuário de QA,  
Quero acessar uma tela dedicada para fazer upload de documento de arquitetura e ver resultados da análise de conformidade,  
Para que possa verificar se o código-fonte está em conformidade com a arquitetura definida.

**Acceptance Criteria:**
1. Tela dedicada implementada com área de upload para documentos de arquitetura
2. Interface drag-and-drop para upload de arquivos de arquitetura (PDF, Markdown, DOCX)
3. Sistema de preview do documento de arquitetura após upload
4. Botão para iniciar análise de conformidade arquitetural usando prompt específico definido na tela de prompts
5. Interface de progresso mostrando status da análise em tempo real
6. Exibição dos resultados da análise de conformidade formatados em Markdown
7. Opção para edição manual dos resultados quando APIs de IA estiverem indisponíveis ou precisa alterar o resultado da análise feita pela IA
8. Botão para download do relatório de conformidade em formato Markdown

**Story 5.3: Business Document Analysis Interface**  
Como um usuário de QA,  
Quero acessar uma tela dedicada para fazer upload de documentos de negócio e ver resultados da análise semântica,  
Para que possa verificar se o código-fonte está alinhado com os requisitos de negócio.

**Acceptance Criteria:**
1. Tela dedicada implementada com área de upload para documentos de negócio
2. Interface drag-and-drop para upload de documentos de negócio (histórias, épicos, regras)
3. Sistema de preview do documento de negócio após upload
4. Botão para iniciar análise semântica de negócio usando prompt específico definido na tela de prompts
5. Interface de progresso mostrando status da análise em tempo real
6. Exibição dos resultados da análise semântica formatados em Markdown
7. Opção para edição manual dos resultados quando APIs de IA estiverem indisponíveis ou precisa alterar o resultado da análise feita pela IA
8. Botão para download do relatório de análise semântica em formato Markdown

**Story 5.4: Analysis Results Integration & Navigation**  
Como um usuário de QA,  
Quero navegar facilmente entre as diferentes telas de análise e ver resultados consolidados,  
Para que tenha uma visão completa e integrada de todas as análises realizadas.

**Acceptance Criteria:**
1. Sistema de navegação entre as três telas de análise implementado
2. A análise é disparada manualmente pelo QA em cada tela e só pode haver uma análise por vez, quando finalizar, habilita para as outras telas

---

## Checklist Results Report

### PM Checklist Validation Report - VerificAI Code Quality System PRD

#### Executive Summary
- **Overall PRD Completeness:** 92% (PASS)
- **MVP Scope Appropriateness:** Just Right
- **Readiness for Architecture Phase:** Ready
- **Most Critical Gaps:** Nenhum bloqueador identificado

#### Category Analysis Table

| Categoria | Status | Critical Issues |
|-----------|--------|----------------|
| 1. Problem Definition & Context | PASS | Nenhum |
| 2. MVP Scope Definition | PASS | Nenhum |
| 3. User Experience Requirements | PASS | Nenhum |
| 4. Functional Requirements | PASS | Nenhum |
| 5. Non-Functional Requirements | PARTIAL | Requisitos de performance específicos |
| 6. Epic & Story Structure | PASS | Nenhum |
| 7. Technical Guidance | PASS | Nenhum |
| 8. Cross-Functional Requirements | PARTIAL | Detalhes de operação |
| 9. Clarity & Communication | PASS | Nenhum |

#### Top Issues by Priority

**HIGH Priority:**
1. **Performance Requirements:** Falta especificar tempos de resposta concretos (ex: < 5s para análise de 200 arquivos)
2. **Operational Requirements:** Monitoramento e alertas precisam ser mais detalhados
3. **Integration Testing:** Faltam requisitos específicos para testes de integração LLM

**MEDIUM Priority:**
1. **Error Handling:** Estratégia de fallback precisa de mais detalhes de implementação
2. **Data Migration:** Schema changes não estão totalmente vinculados a stories específicas

#### MVP Scope Assessment
**✅ Apropriado para MVP:**
- Escopo bem definido e focado no essencial
- Features entregam valor claro ao usuário
- Complexidade gerenciável para 3-4 meses de desenvolvimento
- Separação clara entre MVP e pós-MVP

**Sem features para cortar:** O escopo atual já representa o mínimo viável

#### Technical Readiness
**✅ Excelente preparação:**
- Stack tecnológica claramente definida
- Restrições técnicas bem comunicadas
- Riscos identificados (dependência de LLM APIs)
- Estratégia de GitHub integrada desde o início

#### Recommendations
1. **Adicionar métricas de performance específicas** (tempos de resposta, throughput)
2. **Detalhar estratégia de monitoramento** com métricas específicas para APIs LLM
3. **Expandir requisitos de teste de integração** para componentes LLM
4. **Refinar documentação de operação** para ambiente de produção

#### Final Decision
**✅ READY FOR ARCHITECT**

O PRD está compreensivo, bem estruturado e pronto para a fase de design arquitetural. As questões identificadas são de refinamento e não bloqueiam o progresso.

---

## Next Steps

### UX Expert Prompt

**Contexto:** VerificAI é um sistema de análise de código baseado em IA para equipes de QA. O MVP consiste em 5 telas principais: upload de código, edição de prompts, e 3 telas de análise (critérios gerais, arquitetura, negócio).

**Requisitos de UX:**
- Design System do governo brasileiro (gov.br/ds)
- Interface responsiva para desktop/tablet
- 5 telas principais com drag-and-drop e resultados integrados
- Modo manual para quando APIs de IA estiverem indisponíveis
- WCAG AA compliance

**Tarefa:** Desenvolver uma estratégia de UX completa incluindo wireframes, fluxos de usuário, e especificações detalhadas de interface para as 5 telas do sistema, focando em eficiência para equipes de QA e integração com o Design System governamental.

---

### Architect Prompt

**Contexto:** VerificAI Code Quality System - MVP com backend Python/FastAPI, frontend React/TypeScript, integração com múltiplos LLMs, e análise de código com otimização de tokens. Stack: PostgreSQL, Redis, Docker, GitHub Actions, deploy em Vercel/Cloud Run.

**Requisitos Técnicos:**
- Monorepo structure com GitHub integrado
- Análise de JavaScript/Python/TypeScript (200 arquivos, 5MB max)
- Integração LLM com LangChain e otimização de tokens
- 5 telas principais com upload, análise e resultados integrados
- Modo manual alternativo para falhas de API

**Tarefa:** Desenvolver arquitetura detalhada incluindo estrutura de monorepo, design de APIs, estratégia de integração LLM, otimização de performance, pipeline de CI/CD, e plano de deployment. Focar em escalabilidade, resiliência e preparação para evolução pós-MVP.