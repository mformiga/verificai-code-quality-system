# VerificAI Code Quality System - Full-Stack Architecture Document

---

## Executive Summary

The VerificAI Code Quality System is an AI-powered code analysis platform designed for QA teams, built with a modern full-stack architecture. This document provides a comprehensive technical blueprint covering the entire system architecture, from infrastructure to application components.

### Key Architectural Decisions

1. **Monorepo Structure**: Single repository for frontend, backend, and shared components
2. **Microservice-ready Design**: Monolithic initial deployment with clear boundaries for future microservices
3. **Event-driven Architecture**: Async processing with WebSocket real-time updates
4. **Multi-LLM Integration**: LangChain-based abstraction layer for provider flexibility
5. **Token Optimization Strategy**: Intelligent processing to minimize LLM costs
6. **Gov.br Design System**: Compliance with Brazilian government standards

### System Overview

The system consists of 5 main screens:
1. **Code Upload**: Drag-and-drop interface for code submission
2. **Prompt Configuration**: Management of three analysis prompt types
3. **General Criteria Analysis**: Code quality assessment
4. **Architectural Compliance Analysis**: Architecture document validation
5. **Business Compliance Analysis**: Business requirements validation

---

## 1. Technical Summary and Patterns

### Architecture Patterns

#### 1.1 Clean Architecture
- **Layers**: Domain → Application → Infrastructure → Presentation
- **Dependency Direction**: Outer layers depend on inner layers
- **Domain-driven Design**: Business logic isolated in domain layer

#### 1.2 Event-Driven Architecture
- **Async Processing**: Celery workers for long-running tasks
- **Real-time Updates**: WebSocket connections for progress tracking
- **Event Sourcing**: Analysis state transitions tracked as events

#### 1.3 CQRS Pattern (Command Query Responsibility Segregation)
- **Commands**: Write operations (uploads, configurations, analysis starts)
- **Queries**: Read operations (results, status, history)
- **Separate Models**: Optimized read models for reporting

#### 1.4 Strategy Pattern for LLM Integration
- **Provider Abstraction**: Common interface for different LLM providers
- **Runtime Selection**: Dynamic provider switching based on availability/cost
- **Fallback Mechanisms**: Graceful degradation when providers fail

### Design Patterns Applied

#### 1.5 Repository Pattern
- **Data Access Abstraction**: Clean separation between business logic and data access
- **Testability**: Easy mocking for unit tests
- **Flexibility**: Easy to swap data sources

#### 1.6 Factory Pattern
- **Analysis Type Factory**: Creates appropriate analysis handlers based on type
- **LLM Provider Factory**: Instantiates appropriate LLM clients
- **File Processor Factory**: Creates processors for different file types

#### 1.7 Observer Pattern
- **Progress Tracking**: Multiple components observe analysis progress
- **Status Updates**: Real-time notifications via WebSocket
- **State Synchronization**: Frontend components react to backend state changes

---

## 2. Complete Technology Stack

### 2.1 Frontend Stack

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **Framework** | React | 18.3.1 | UI Framework |
| **Language** | TypeScript | 5.6.3 | Type Safety |
| **Build Tool** | Vite | 5.4.10 | Fast Development & Build |
| **State Management** | Zustand | 4.5.5 | Lightweight State Store |
| **HTTP Client** | Axios | 1.7.7 | API Communication |
| **Routing** | React Router | 6.26.1 | SPA Navigation |
| **UI Library** | Tailwind CSS | 3.4.13 | Utility-first CSS |
| **Design System** | gov.br/ds | 2.0 | Brazilian Government Standards |
| **Form Handling** | React Hook Form | 7.53.1 | Form Management |
| **Validation** | Zod | 3.23.8 | Schema Validation |
| **Testing** | Vitest | 2.1.4 | Unit Testing |
| **E2E Testing** | Playwright | 1.40+ | End-to-End Testing |

### 2.2 Backend Stack

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **Framework** | FastAPI | 0.104.1+ | High-performance API Framework |
| **Language** | Python | 3.11+ | Core Language |
| **Database** | PostgreSQL | 15.0+ | Primary Database |
| **Cache** | Redis | 7.0+ | In-memory Cache & Session Store |
| **ORM** | SQLAlchemy | 2.0+ | Database ORM |
| **Task Queue** | Celery | 5.3+ | Async Task Processing |
| **LLM Integration** | LangChain | 0.1+ | LLM Abstraction Layer |
| **WebSocket** | FastAPI WebSocket | Built-in | Real-time Communication |
| **Authentication** | FastAPI Auth | JWT | Token-based Auth |
| **Rate Limiting** | SlowAPI | - | API Rate Limiting |

### 2.3 DevOps & Infrastructure

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Containerization** | Docker | Application Containerization |
| **Orchestration** | Docker Compose | Local Development |
| **CI/CD** | GitHub Actions | Continuous Integration/Deployment |
| **Cloud Provider** | Vercel/Cloud Run | Production Deployment |
| **Monitoring** | Prometheus/Grafana | System Monitoring |
| **Logging** | Structured Logging | Application Logging |
| **Secrets Management** | GitHub Secrets | Secure Configuration |

### 2.4 External Integrations

| Service | Purpose |
|---------|---------|
| **OpenAI API** | GPT models for code analysis |
| **Anthropic Claude** | Alternative LLM provider |
| **Google Gemini** | Additional LLM provider |
| **GitHub API** | Repository integration (future) |
| **Analytics** | Google Analytics | Usage tracking |

---

## 3. Data Models and Relationships

### 3.1 Core Entity-Relationship Diagram

```
User (1) ←→ (N) AnalysisSession
    ↓           ↓
Configuration (N) ←→ (1) AnalysisType
    ↓           ↓
    (N) ←→ FileUpload
    ↓           ↓
    (N) ←→ AnalysisResult
```

### 3.2 Database Schema

#### 3.2.1 Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50) DEFAULT 'user',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
```

#### 3.2.2 Analysis Sessions Table
```sql
CREATE TABLE analysis_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    session_name VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'created', -- created, processing, completed, failed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    total_files INTEGER DEFAULT 0,
    processed_files INTEGER DEFAULT 0
);

CREATE INDEX idx_analysis_sessions_user_id ON analysis_sessions(user_id);
CREATE INDEX idx_analysis_sessions_status ON analysis_sessions(status);
CREATE INDEX idx_analysis_sessions_created_at ON analysis_sessions(created_at);
```

#### 3.2.3 Configurations Table
```sql
CREATE TABLE configurations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    config_type VARCHAR(50) NOT NULL, -- general, architectural, business
    prompt_content TEXT NOT NULL,
    is_default BOOLEAN DEFAULT false,
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_configurations_user_id ON configurations(user_id);
CREATE INDEX idx_configurations_type ON configurations(config_type);
```

#### 3.2.4 File Uploads Table
```sql
CREATE TABLE file_uploads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_session_id UUID REFERENCES analysis_sessions(id) ON DELETE CASCADE,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size BIGINT NOT NULL,
    file_type VARCHAR(100) NOT NULL,
    upload_status VARCHAR(50) DEFAULT 'uploaded',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_file_uploads_session_id ON file_uploads(analysis_session_id);
CREATE INDEX idx_file_uploads_type ON file_uploads(file_type);
```

#### 3.2.5 Analysis Results Table
```sql
CREATE TABLE analysis_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_session_id UUID REFERENCES analysis_sessions(id) ON DELETE CASCADE,
    configuration_id UUID REFERENCES configurations(id),
    analysis_type VARCHAR(50) NOT NULL,
    file_name VARCHAR(255),
    result_content TEXT NOT NULL,
    score DECIMAL(5,2),
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_analysis_results_session_id ON analysis_results(analysis_session_id);
CREATE INDEX idx_analysis_results_type ON analysis_results(analysis_type);
CREATE INDEX idx_analysis_results_status ON analysis_results(status);
```

#### 3.2.6 Analysis Tasks Table (for Celery)
```sql
CREATE TABLE analysis_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_session_id UUID REFERENCES analysis_sessions(id) ON DELETE CASCADE,
    task_id VARCHAR(255) UNIQUE NOT NULL, -- Celery task ID
    task_type VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending', -- pending, running, completed, failed
    progress INTEGER DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP NULL,
    completed_at TIMESTAMP NULL
);

CREATE INDEX idx_analysis_tasks_session_id ON analysis_tasks(analysis_session_id);
CREATE INDEX idx_analysis_tasks_task_id ON analysis_tasks(task_id);
CREATE INDEX idx_analysis_tasks_status ON analysis_tasks(status);
```

### 3.3 TypeScript Types

```typescript
// shared/types/index.ts
export interface User {
  id: string;
  email: string;
  fullName: string;
  role: 'user' | 'admin';
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface AnalysisSession {
  id: string;
  userId: string;
  sessionName: string;
  status: 'created' | 'processing' | 'completed' | 'failed';
  createdAt: string;
  updatedAt: string;
  completedAt?: string;
  totalFiles: number;
  processedFiles: number;
}

export interface Configuration {
  id: string;
  userId: string;
  configType: 'general' | 'architectural' | 'business';
  promptContent: string;
  isDefault: boolean;
  version: number;
  createdAt: string;
  updatedAt: string;
}

export interface FileUpload {
  id: string;
  analysisSessionId: string;
  fileName: string;
  filePath: string;
  fileSize: number;
  fileType: string;
  uploadStatus: 'uploaded' | 'processing' | 'completed' | 'failed';
  createdAt: string;
}

export interface AnalysisResult {
  id: string;
  analysisSessionId: string;
  configurationId: string;
  analysisType: 'general' | 'architectural' | 'business';
  fileName?: string;
  resultContent: string;
  score?: number;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  createdAt: string;
  updatedAt: string;
}

export interface AnalysisTask {
  id: string;
  analysisSessionId: string;
  taskId: string;
  taskType: 'general_analysis' | 'architectural_analysis' | 'business_analysis';
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress: number;
  errorMessage?: string;
  createdAt: string;
  startedAt?: string;
  completedAt?: string;
}
```

---

## 4. Component Design

### 4.1 Frontend Component Architecture

#### 4.1.1 Page Components

```
src/
├── pages/
│   ├── DashboardPage.tsx           # Main dashboard with session overview
│   ├── CodeUploadPage.tsx          # Code file upload interface
│   ├── PromptConfigPage.tsx       # Prompt management interface
│   ├── GeneralAnalysisPage.tsx     # General criteria analysis
│   ├── ArchitecturalAnalysisPage.tsx # Architecture compliance analysis
│   ├── BusinessAnalysisPage.tsx    # Business compliance analysis
│   └── SettingsPage.tsx            # User settings
```

#### 4.1.2 Feature Components

```
src/components/features/
├── Upload/
│   ├── FileUpload.tsx              # Main upload component
│   ├── DragDropZone.tsx           # Drag-and-drop area
│   ├── FileList.tsx               # Uploaded files list
│   └── UploadProgress.tsx         # Upload progress indicator
├── Analysis/
│   ├── AnalysisResults.tsx        # Results display component
│   ├── AnalysisProgress.tsx       # Analysis progress tracking
│   ├── ResultsTable.tsx           # Tabular results view
│   └── ReportViewer.tsx           # Markdown report viewer
├── Configuration/
│   ├── PromptEditor.tsx           # Prompt editing interface
│   ├── ConfigForm.tsx             # Configuration form
│   └── ConfigHistory.tsx          # Configuration version history
└── Common/
    ├── StatusBar.tsx              # System status indicator
    ├── NotificationPanel.tsx      # Notifications center
    └── SessionManager.tsx         # Session management
```

#### 4.1.3 Shared Components

```
src/components/common/
├── Layout/
│   ├── Header.tsx                 # Application header
│   ├── Sidebar.tsx                # Navigation sidebar
│   └── Footer.tsx                 # Application footer
├── UI/
│   ├── Button.tsx                 # Reusable button component
│   ├── Input.tsx                  # Form input component
│   ├── Modal.tsx                  # Modal dialog component
│   ├── Card.tsx                   # Card container component
│   └── Badge.tsx                  # Status badge component
├── Forms/
│   ├── FormField.tsx              # Form field wrapper
│   ├── FileInput.tsx              # File input component
│   └── Select.tsx                 # Select dropdown component
└── Feedback/
    ├── LoadingSpinner.tsx         # Loading indicator
    ├── ErrorMessage.tsx           # Error message display
    └── SuccessMessage.tsx          # Success message display
```

### 4.2 Backend Component Architecture

#### 4.2.1 API Layer

```
backend/app/
├── api/
│   ├── v1/
│   │   ├── endpoints/
│   │   │   ├── auth.py            # Authentication endpoints
│   │   │   ├── users.py           # User management
│   │   │   ├── sessions.py        # Analysis sessions
│   │   │   ├── configurations.py  # Prompt configurations
│   │   │   ├── uploads.py         # File uploads
│   │   │   ├── analysis.py        # Analysis operations
│   │   │   └── websocket.py       # WebSocket endpoints
│   │   └── dependencies.py        # FastAPI dependencies
│   └── websocket/
│       ├── manager.py             # WebSocket connection manager
│       └── handlers.py            # WebSocket message handlers
```

#### 4.2.2 Core Services

```
backend/app/core/
├── services/
│   ├── analysis_service.py       # Main analysis orchestration
│   ├── file_service.py           # File processing service
│   ├── llm_service.py            # LLM integration service
│   ├── config_service.py         # Configuration management
│   └── auth_service.py           # Authentication service
├── workers/
│   ├── celery_app.py             # Celery application setup
│   ├── analysis_tasks.py         # Analysis task workers
│   └── file_processor.py         # File processing workers
└── utils/
    ├── file_utils.py             # File operation utilities
    ├── token_optimizer.py        # LLM token optimization
    └── security_utils.py         # Security utilities
```

#### 4.2.3 Data Layer

```
backend/app/
├── models/
│   ├── base.py                   # Base model class
│   ├── user.py                   # User models
│   ├── session.py                # Session models
│   ├── configuration.py          # Configuration models
│   ├── upload.py                 # Upload models
│   └── analysis.py               # Analysis models
├── repositories/
│   ├── user_repository.py        # User data access
│   ├── session_repository.py     # Session data access
│   ├── config_repository.py      # Configuration data access
│   └── analysis_repository.py    # Analysis data access
└── database/
    ├── connection.py             # Database connection
    ├── migrations/               # Database migrations
    └── seed_data.py              # Initial data seeding
```

### 4.3 Component Interaction Patterns

#### 4.3.1 Frontend State Flow

```typescript
// Example state management pattern
interface AnalysisState {
  currentSession: AnalysisSession | null;
  uploadedFiles: FileUpload[];
  analysisResults: AnalysisResult[];
  isLoading: boolean;
  error: string | null;
}

const useAnalysisStore = create<AnalysisState>((set, get) => ({
  currentSession: null,
  uploadedFiles: [],
  analysisResults: [],
  isLoading: false,
  error: null,

  startAnalysis: async (sessionId: string) => {
    set({ isLoading: true, error: null });
    try {
      const results = await analysisService.startAnalysis(sessionId);
      set({ analysisResults: results, isLoading: false });
    } catch (error) {
      set({ error: error.message, isLoading: false });
    }
  },

  // ... other actions
}));
```

#### 4.3.2 Backend Service Pattern

```python
# Example service pattern
class AnalysisService:
    def __init__(
        self,
        session_repository: SessionRepository,
        llm_service: LLMService,
        file_service: FileService
    ):
        self.session_repository = session_repository
        self.llm_service = llm_service
        self.file_service = file_service

    async def start_analysis(
        self,
        session_id: str,
        analysis_type: str
    ) -> AnalysisResult:
        # Business logic here
        session = await self.session_repository.get_by_id(session_id)
        if not session:
            raise ValueError("Session not found")

        # Create analysis task
        task = await self.create_analysis_task(session_id, analysis_type)

        # Queue task for processing
        await self.queue_analysis_task(task.id)

        return task
```

---

## 5. External API Integrations

### 5.1 LLM Provider Integration

#### 5.1.1 LangChain Configuration

```python
# backend/app/core/services/llm_service.py
from langchain.chat_models import ChatOpenAI, ChatAnthropic, ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage
from langchain.callbacks.base import BaseCallbackHandler
from typing import Dict, Any, List, Optional
import asyncio
import logging

class LLMService:
    def __init__(self):
        self.providers = {
            'openai': ChatOpenAI,
            'anthropic': ChatAnthropic,
            'google': ChatGoogleGenerativeAI
        }
        self.current_provider = 'openai'
        self.fallback_providers = ['anthropic', 'google']

    async def analyze_code(
        self,
        code: str,
        prompt: str,
        analysis_type: str,
        callback_handler: Optional[BaseCallbackHandler] = None
    ) -> str:
        """Analyze code using LLM with fallback mechanism"""

        for provider_name in [self.current_provider] + self.fallback_providers:
            try:
                provider = self._get_provider(provider_name)
                messages = self._build_messages(code, prompt, analysis_type)

                response = await asyncio.to_thread(
                    provider.invoke,
                    messages,
                    callbacks=[callback_handler] if callback_handler else None
                )

                return response.content

            except Exception as e:
                logging.error(f"Provider {provider_name} failed: {e}")
                continue

        raise RuntimeError("All LLM providers failed")

    def _get_provider(self, provider_name: str):
        """Get configured LLM provider instance"""
        provider_class = self.providers[provider_name]

        if provider_name == 'openai':
            return provider_class(
                model="gpt-4",
                temperature=0.1,
                max_tokens=4000
            )
        elif provider_name == 'anthropic':
            return provider_class(
                model="claude-3-sonnet-20240229",
                temperature=0.1,
                max_tokens=4000
            )
        elif provider_name == 'google':
            return provider_class(
                model="gemini-pro",
                temperature=0.1,
                max_tokens=4000
            )

    def _build_messages(self, code: str, prompt: str, analysis_type: str) -> List:
        """Build message structure for LLM"""
        system_message = SystemMessage(
            content=f"You are an expert code analyst specializing in {analysis_type} analysis."
        )

        human_message = HumanMessage(
            content=f"""{prompt}

Code to analyze:
```python
{code}
```

Please provide a detailed analysis following the specified criteria."""
        )

        return [system_message, human_message]
```

#### 5.1.2 Token Optimization Strategy

```python
# backend/app/core/utils/token_optimizer.py
import re
import tiktoken
from typing import List, Tuple
from dataclasses import dataclass

@dataclass
class TokenOptimizationResult:
    optimized_content: str
    token_count: int
    compression_ratio: float

class TokenOptimizer:
    def __init__(self, model: str = "gpt-4"):
        self.encoder = tiktoken.encoding_for_model(model)
        self.max_tokens = 8000  # Conservative limit
        self.target_tokens = 6000  # Target for optimization

    def optimize_code(self, code: str) -> TokenOptimizationResult:
        """Optimize code content for LLM processing"""
        original_tokens = len(self.encoder.encode(code))

        if original_tokens <= self.target_tokens:
            return TokenOptimizationResult(
                optimized_content=code,
                token_count=original_tokens,
                compression_ratio=1.0
            )

        # Apply optimization strategies
        optimized = self._apply_optimizations(code)
        final_tokens = len(self.encoder.encode(optimized))

        return TokenOptimizationResult(
            optimized_content=optimized,
            token_count=final_tokens,
            compression_ratio=final_tokens / original_tokens
        )

    def _apply_optimizations(self, code: str) -> str:
        """Apply multiple optimization strategies"""
        # Strategy 1: Remove comments
        code = self._remove_comments(code)

        # Strategy 2: Remove empty lines
        code = self._remove_empty_lines(code)

        # Strategy 3: Minify whitespace
        code = self._minify_whitespace(code)

        # Strategy 4: Remove imports if too large
        if len(self.encoder.encode(code)) > self.max_tokens:
            code = self._remove_imports(code)

        # Strategy 5: Split into chunks if still too large
        if len(self.encoder.encode(code)) > self.max_tokens:
            code = self._create_chunked_summary(code)

        return code

    def _remove_comments(self, code: str) -> str:
        """Remove single-line and multi-line comments"""
        # Remove single-line comments
        code = re.sub(r'#.*$', '', code, flags=re.MULTILINE)
        # Remove multi-line comments
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
        return code

    def _remove_empty_lines(self, code: str) -> str:
        """Remove excessive empty lines"""
        return re.sub(r'\n\s*\n', '\n', code)

    def _minify_whitespace(self, code: str) -> str:
        """Reduce whitespace while preserving structure"""
        lines = code.split('\n')
        minified_lines = []

        for line in lines:
            # Remove leading/trailing whitespace but preserve indentation
            minified_line = line.rstrip()
            minified_lines.append(minified_line)

        return '\n'.join(minified_lines)

    def _remove_imports(self, code: str) -> str:
        """Remove import statements to save tokens"""
        lines = code.split('\n')
        filtered_lines = []
        skip_imports = False

        for line in lines:
            if line.strip().startswith(('import ', 'from ')):
                if not skip_imports:
                    filtered_lines.append("# [Imports section removed for token optimization]")
                    skip_imports = True
            else:
                skip_imports = False
                filtered_lines.append(line)

        return '\n'.join(filtered_lines)

    def _create_chunked_summary(self, code: str) -> str:
        """Create a summary when code is too large"""
        lines = code.split('\n')
        total_lines = len(lines)

        # Take first 100 lines and last 50 lines
        header_lines = lines[:100]
        footer_lines = lines[-50:] if total_lines > 150 else []

        result = []
        result.extend(header_lines)

        if footer_lines:
            result.append(f"\n# ... {total_lines - len(header_lines) - len(footer_lines)} lines omitted ...")
            result.extend(footer_lines)

        return '\n'.join(result)
```

### 5.2 API Rate Limiting and Error Handling

```python
# backend/app/core/middleware/rate_limiter.py
from fastapi import Request, Response, HTTPException
from fastapi.middleware import Middleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import time

class RateLimiter:
    def __init__(self):
        self.limiter = Limiter(key_func=get_remote_address)
        self.requests = {}

    async def __call__(self, request: Request, call_next):
        client_ip = get_remote_address(request)
        endpoint = request.url.path

        # Different limits for different endpoints
        if endpoint.startswith('/api/analysis'):
            limit = 10  # 10 requests per minute
        elif endpoint.startswith('/api/upload'):
            limit = 5   # 5 uploads per minute
        else:
            limit = 100 # General API calls

        current_time = time.time()
        key = f"{client_ip}:{endpoint}"

        # Clean old requests
        self.requests[key] = [
            req_time for req_time in self.requests.get(key, [])
            if current_time - req_time < 60
        ]

        # Check limit
        if len(self.requests[key]) >= limit:
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please try again later."
            )

        # Add current request
        self.requests[key].append(current_time)

        try:
            response = await call_next(request)
            return response
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
```

---

## 6. REST API Specification

### 6.1 API Versioning Strategy

- **Base URL**: `/api/v1`
- **Content-Type**: `application/json`
- **Authentication**: Bearer token (JWT)
- **Rate Limiting**: Endpoint-specific limits

### 6.2 Authentication Endpoints

#### 6.2.1 Login
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}

Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "John Doe",
    "role": "user"
  }
}
```

#### 6.2.2 Register
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123",
  "full_name": "John Doe"
}

Response:
{
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "John Doe",
    "role": "user"
  }
}
```

### 6.3 Session Management

#### 6.3.1 Create Analysis Session
```http
POST /api/v1/sessions
Authorization: Bearer <token>
Content-Type: application/json

{
  "session_name": "E-commerce Platform Analysis"
}

Response:
{
  "id": "uuid",
  "user_id": "uuid",
  "session_name": "E-commerce Platform Analysis",
  "status": "created",
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z",
  "total_files": 0,
  "processed_files": 0
}
```

#### 6.3.2 Get Sessions
```http
GET /api/v1/sessions?page=1&limit=10
Authorization: Bearer <token>

Response:
{
  "sessions": [...],
  "total": 25,
  "page": 1,
  "limit": 10,
  "total_pages": 3
}
```

### 6.4 File Upload

#### 6.4.1 Upload Files
```http
POST /api/v1/upload/{session_id}
Authorization: Bearer <token>
Content-Type: multipart/form-data

form-data:
- files: [file1, file2, ...]
- override_existing: false

Response:
{
  "uploaded_files": [
    {
      "id": "uuid",
      "file_name": "app.py",
      "file_size": 1024,
      "file_type": "text/x-python",
      "upload_status": "uploaded",
      "created_at": "2023-01-01T00:00:00Z"
    }
  ],
  "session_id": "uuid"
}
```

### 6.5 Configuration Management

#### 6.5.1 Save Configuration
```http
POST /api/v1/configurations
Authorization: Bearer <token>
Content-Type: application/json

{
  "config_type": "general",
  "prompt_content": "Analyze the code for best practices...",
  "is_default": false
}

Response:
{
  "id": "uuid",
  "user_id": "uuid",
  "config_type": "general",
  "prompt_content": "Analyze the code for best practices...",
  "is_default": false,
  "version": 1,
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z"
}
```

#### 6.5.2 Get Configurations
```http
GET /api/v1/configurations?type=general
Authorization: Bearer <token>

Response:
{
  "configurations": [...]
}
```

### 6.6 Analysis Operations

#### 6.6.1 Start Analysis
```http
POST /api/v1/analysis/{session_id}/start
Authorization: Bearer <token>
Content-Type: application/json

{
  "analysis_type": "general",
  "configuration_id": "uuid"
}

Response:
{
  "task_id": "celery-task-uuid",
  "session_id": "uuid",
  "analysis_type": "general",
  "status": "pending",
  "created_at": "2023-01-01T00:00:00Z"
}
```

#### 6.6.2 Get Analysis Results
```http
GET /api/v1/analysis/{session_id}/results
Authorization: Bearer <token>

Response:
{
  "results": [
    {
      "id": "uuid",
      "analysis_type": "general",
      "file_name": "app.py",
      "result_content": "## Analysis Results\n...",
      "score": 8.5,
      "status": "completed",
      "created_at": "2023-01-01T00:00:00Z",
      "updated_at": "2023-01-01T00:00:00Z"
    }
  ]
}
```

#### 6.6.3 Get Analysis Status
```http
GET /api/v1/analysis/{session_id}/status
Authorization: Bearer <token>

Response:
{
  "session_id": "uuid",
  "status": "processing",
  "progress": 65,
  "total_files": 10,
  "processed_files": 7,
  "current_task": "Processing file: utils.py",
  "estimated_time_remaining": 120
}
```

### 6.7 WebSocket Events

#### 6.7.1 Analysis Progress Updates
```json
{
  "type": "analysis_progress",
  "session_id": "uuid",
  "progress": {
    "current": 7,
    "total": 10,
    "percentage": 70,
    "current_file": "utils.py"
  }
}
```

#### 6.7.2 Analysis Results
```json
{
  "type": "analysis_result",
  "session_id": "uuid",
  "result": {
    "file_name": "utils.py",
    "content": "## Analysis Results\n...",
    "score": 8.5
  }
}
```

#### 6.7.3 Analysis Complete
```json
{
  "type": "analysis_complete",
  "session_id": "uuid",
  "summary": {
    "total_files": 10,
    "processed_files": 10,
    "average_score": 8.2,
    "duration": 180
  }
}
```

---

## 7. Database Schema Implementation

### 7.1 SQLAlchemy Models

```python
# backend/app/models/base.py
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, DateTime, Boolean
from datetime import datetime
import uuid

Base = declarative_base()

class BaseModel(Base):
    __abstract__ = True

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# backend/app/models/user.py
from sqlalchemy import Column, String, Boolean
from .base import BaseModel

class User(BaseModel):
    __tablename__ = "users"

    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    role = Column(String(50), default="user")
    is_active = Column(Boolean, default=True)

# backend/app/models/session.py
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .base import BaseModel

class AnalysisSession(BaseModel):
    __tablename__ = "analysis_sessions"

    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    session_name = Column(String(255), nullable=False)
    status = Column(String(50), default="created")
    completed_at = Column(DateTime, nullable=True)
    total_files = Column(Integer, default=0)
    processed_files = Column(Integer, default=0)

    # Relationships
    user = relationship("User", back_populates="sessions")
    files = relationship("FileUpload", back_populates="session", cascade="all, delete-orphan")
    results = relationship("AnalysisResult", back_populates="session", cascade="all, delete-orphan")
    tasks = relationship("AnalysisTask", back_populates="session", cascade="all, delete-orphan")

# backend/app/models/configuration.py
from sqlalchemy import Column, String, Text, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel

class Configuration(BaseModel):
    __tablename__ = "configurations"

    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    config_type = Column(String(50), nullable=False)
    prompt_content = Column(Text, nullable=False)
    is_default = Column(Boolean, default=False)
    version = Column(Integer, default=1)

    # Relationships
    user = relationship("User", back_populates="configurations")
    results = relationship("AnalysisResult", back_populates="configuration")

# backend/app/models/upload.py
from sqlalchemy import Column, String, BigInteger, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel

class FileUpload(BaseModel):
    __tablename__ = "file_uploads"

    analysis_session_id = Column(String, ForeignKey("analysis_sessions.id"), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(BigInteger, nullable=False)
    file_type = Column(String(100), nullable=False)
    upload_status = Column(String(50), default="uploaded")

    # Relationships
    session = relationship("AnalysisSession", back_populates="files")

# backend/app/models/analysis.py
from sqlalchemy import Column, String, Text, ForeignKey, Numeric, String
from sqlalchemy.orm import relationship
from .base import BaseModel

class AnalysisResult(BaseModel):
    __tablename__ = "analysis_results"

    analysis_session_id = Column(String, ForeignKey("analysis_sessions.id"), nullable=False)
    configuration_id = Column(String, ForeignKey("configurations.id"), nullable=True)
    analysis_type = Column(String(50), nullable=False)
    file_name = Column(String(255), nullable=True)
    result_content = Column(Text, nullable=False)
    score = Column(Numeric(5, 2), nullable=True)
    status = Column(String(50), default="pending")

    # Relationships
    session = relationship("AnalysisSession", back_populates="results")
    configuration = relationship("Configuration", back_populates="results")

class AnalysisTask(BaseModel):
    __tablename__ = "analysis_tasks"

    analysis_session_id = Column(String, ForeignKey("analysis_sessions.id"), nullable=False)
    task_id = Column(String(255), unique=True, nullable=False)
    task_type = Column(String(50), nullable=False)
    status = Column(String(50), default="pending")
    progress = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    session = relationship("AnalysisSession", back_populates="tasks")
```

### 7.2 Database Migrations

```python
# backend/app/database/migrations/versions/001_initial_tables.py
"""Initial tables migration

Revision ID: 001
Revises:
Create Date: 2023-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=True),
        sa.Column('role', sa.String(length=50), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )

    # Create analysis_sessions table
    op.create_table('analysis_sessions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('session_name', sa.String(length=255), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('total_files', sa.Integer(), nullable=True),
        sa.Column('processed_files', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create other tables...
    # (Similar structure for configurations, file_uploads, analysis_results, analysis_tasks)

def downgrade():
    # Drop tables in reverse order
    op.drop_table('analysis_tasks')
    op.drop_table('analysis_results')
    op.drop_table('file_uploads')
    op.drop_table('configurations')
    op.drop_table('analysis_sessions')
    op.drop_table('users')
```

### 7.3 Database Connection and Session Management

```python
# backend/app/database/connection.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
import os

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://verificai:verificai123@localhost:5432/verificai")

# Create engine
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=300
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

def get_db() -> Session:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def get_db_context():
    """Context manager for database sessions"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

## 8. Source Tree Structure

### 8.1 Complete Project Structure

```
verificai-code-quality-system/
├── README.md
├── .gitignore
├── docker-compose.yml
├── .env.example
├── package.json
├── package-lock.json
├── .github/
│   ├── workflows/
│   │   ├── ci.yml
│   │   ├── deploy.yml
│   │   └── code-quality.yml
│   └── ISSUE_TEMPLATE/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI application entry point
│   │   ├── config.py               # Application configuration
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── endpoints/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── auth.py
│   │   │   │   │   ├── users.py
│   │   │   │   │   ├── sessions.py
│   │   │   │   │   ├── configurations.py
│   │   │   │   │   ├── uploads.py
│   │   │   │   │   └── analysis.py
│   │   │   │   └── dependencies.py
│   │   │   └── websocket/
│   │   │       ├── __init__.py
│   │   │       ├── manager.py
│   │   │       └── handlers.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── services/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── analysis_service.py
│   │   │   │   ├── auth_service.py
│   │   │   │   ├── config_service.py
│   │   │   │   ├── file_service.py
│   │   │   │   └── llm_service.py
│   │   │   ├── workers/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── celery_app.py
│   │   │   │   ├── analysis_tasks.py
│   │   │   │   └── file_processor.py
│   │   │   └── utils/
│   │   │       ├── __init__.py
│   │   │       ├── file_utils.py
│   │   │       ├── security_utils.py
│   │   │       └── token_optimizer.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── user.py
│   │   │   ├── session.py
│   │   │   ├── configuration.py
│   │   │   ├── upload.py
│   │   │   └── analysis.py
│   │   ├── repositories/
│   │   │   ├── __init__.py
│   │   │   ├── base_repository.py
│   │   │   ├── user_repository.py
│   │   │   ├── session_repository.py
│   │   │   ├── config_repository.py
│   │   │   └── analysis_repository.py
│   │   ├── database/
│   │   │   ├── __init__.py
│   │   │   ├── connection.py
│   │   │   └── migrations/
│   │   │       ├── versions/
│   │   │       └── script.py.mako
│   │   ├── middleware/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── cors.py
│   │   │   └── rate_limiter.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── session.py
│   │   │   ├── configuration.py
│   │   │   ├── upload.py
│   │   │   └── analysis.py
│   │   └── static/
│   │       └── uploads/
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── unit/
│   │   │   ├── __init__.py
│   │   │   ├── test_services/
│   │   │   ├── test_models/
│   │   │   └── test_repositories/
│   │   ├── integration/
│   │   │   ├── __init__.py
│   │   │   ├── test_api/
│   │   │   └── test_database/
│   │   └── e2e/
│   │       ├── __init__.py
│   │       └── test_analysis_flow.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── .env.example
│   └── alembic.ini
├── frontend/
│   ├── src/
│   │   ├── __init__.ts
│   │   ├── main.tsx                   # Application entry point
│   │   ├── App.tsx                    # Root component
│   │   ├── router.tsx                 # Routing configuration
│   │   ├── components/
│   │   │   ├── common/
│   │   │   │   ├── Layout/
│   │   │   │   │   ├── Header.tsx
│   │   │   │   │   ├── Sidebar.tsx
│   │   │   │   │   └── Footer.tsx
│   │   │   │   ├── UI/
│   │   │   │   │   ├── Button.tsx
│   │   │   │   │   ├── Input.tsx
│   │   │   │   │   ├── Card.tsx
│   │   │   │   │   ├── Modal.tsx
│   │   │   │   │   └── Badge.tsx
│   │   │   │   ├── Forms/
│   │   │   │   │   ├── FileUpload.tsx
│   │   │   │   │   ├── PromptEditor.tsx
│   │   │   │   │   └── AnalysisConfig.tsx
│   │   │   │   └── Feedback/
│   │   │   │       ├── LoadingSpinner.tsx
│   │   │   │       ├── ErrorMessage.tsx
│   │   │   │       └── SuccessMessage.tsx
│   │   │   ├── features/
│   │   │   │   ├── Upload/
│   │   │   │   │   ├── FileUpload.tsx
│   │   │   │   │   ├── DragDropZone.tsx
│   │   │   │   │   ├── FileList.tsx
│   │   │   │   │   └── UploadProgress.tsx
│   │   │   │   ├── Analysis/
│   │   │   │   │   ├── AnalysisResults.tsx
│   │   │   │   │   ├── AnalysisProgress.tsx
│   │   │   │   │   ├── ResultsTable.tsx
│   │   │   │   │   └── ReportViewer.tsx
│   │   │   │   ├── Configuration/
│   │   │   │   │   ├── PromptEditor.tsx
│   │   │   │   │   ├── ConfigForm.tsx
│   │   │   │   │   └── ConfigHistory.tsx
│   │   │   │   └── Common/
│   │   │   │       ├── StatusBar.tsx
│   │   │   │       ├── NotificationPanel.tsx
│   │   │   │       └── SessionManager.tsx
│   │   │   └── layout/
│   │   │       ├── MainLayout.tsx
│   │   │       └── AuthLayout.tsx
│   │   ├── pages/
│   │   │   ├── DashboardPage.tsx
│   │   │   ├── CodeUploadPage.tsx
│   │   │   ├── PromptConfigPage.tsx
│   │   │   ├── GeneralAnalysisPage.tsx
│   │   │   ├── ArchitecturalAnalysisPage.tsx
│   │   │   ├── BusinessAnalysisPage.tsx
│   │   │   ├── SettingsPage.tsx
│   │   │   └── NotFoundPage.tsx
│   │   ├── hooks/
│   │   │   ├── useApi.ts
│   │   │   ├── useFileUpload.ts
│   │   │   ├── useAnalysis.ts
│   │   │   ├── usePromptConfig.ts
│   │   │   ├── useWebSocket.ts
│   │   │   └── useAuth.ts
│   │   ├── stores/
│   │   │   ├── authStore.ts
│   │   │   ├── analysisStore.ts
│   │   │   ├── uploadStore.ts
│   │   │   └── promptStore.ts
│   │   ├── services/
│   │   │   ├── apiClient.ts
│   │   │   ├── authService.ts
│   │   │   ├── analysisService.ts
│   │   │   ├── fileService.ts
│   │   │   └── configService.ts
│   │   ├── utils/
│   │   │   ├── validation.ts
│   │   │   ├── formatting.ts
│   │   │   ├── constants.ts
│   │   │   ├── helpers.ts
│   │   │   └── sanitization.ts
│   │   ├── types/
│   │   │   ├── api.ts
│   │   │   ├── analysis.ts
│   │   │   ├── file.ts
│   │   │   └── prompt.ts
│   │   └── assets/
│   │       ├── images/
│   │       │   ├── logo.svg
│   │       │   └── favicon.ico
│   │       └── styles/
│   │           ├── globals.css
│   │           └── variables.css
│   ├── tests/
│   │   ├── __init__.ts
│   │   ├── components/
│   │   │   ├── common/
│   │   │   ├── features/
│   │   │   └── pages/
│   │   ├── hooks/
│   │   ├── services/
│   │   ├── utils/
│   │   └── setup.ts
│   ├── public/
│   │   ├── favicon.ico
│   │   ├── manifest.json
│   │   └── robots.txt
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   ├── eslint.config.js
│   ├── .env.example
│   ├── Dockerfile
│   └── package.json
├── shared/
│   ├── types/
│   │   ├── index.ts
│   │   ├── api.ts
│   │   ├── analysis.ts
│   │   └── common.ts
│   ├── constants/
│   │   ├── index.ts
│   │   ├── analysis.ts
│   │   └── api.ts
│   └── utils/
│       ├── validation.ts
│       └── formatting.ts
├── docs/
│   ├── architecture.md
│   ├── frontend-architecture.md
│   ├── prd.md
│   ├── ui-ux-specification.md
│   ├── api-documentation.md
│   ├── deployment-guide.md
│   └── contributing.md
├── tests/
│   ├── e2e/
│   │   ├── analysis-flow.spec.ts
│   │   ├── upload-flow.spec.ts
│   │   └── auth-flow.spec.ts
│   └── performance/
│       ├── load-test.js
│       └── performance-monitoring.py
└── infrastructure/
    ├── terraform/
    │   ├── main.tf
    │   ├── variables.tf
    │   └── outputs.tf
    ├── kubernetes/
    │   ├── backend-deployment.yaml
    │   ├── frontend-deployment.yaml
    │   ├── postgres-deployment.yaml
    │   └── redis-deployment.yaml
    └── monitoring/
        ├── prometheus.yml
        ├── grafana-dashboard.json
        └── alertmanager.yml
```

---

## 9. Infrastructure and Deployment

### 9.1 Container Architecture

#### 9.1.1 Docker Configuration

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```dockerfile
# frontend/Dockerfile
FROM node:18-alpine AS base

# Install dependencies only when needed
FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app

# Install dependencies based on the preferred package manager
COPY package.json package-lock.json* ./
RUN npm ci

# Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Build the application
RUN npm run build

# Production image, copy all the files and run next
FROM base AS runner
WORKDIR /app

ENV NODE_ENV production
ENV NEXT_TELEMETRY_DISABLED 1

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public

# Set the correct permission for prerender cache
RUN mkdir .next
RUN chown nextjs:nodejs .next

# Automatically leverage output traces to reduce image size
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT 3000
ENV HOSTNAME "0.0.0.0"

CMD ["node", "server.js"]
```

#### 9.1.2 Docker Compose Development

```yaml
# docker-compose.yml (development)
version: '3.8'

services:
  # PostgreSQL Database
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: verificai
      POSTGRES_USER: verificai
      POSTGRES_PASSWORD: verificai123
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    networks:
      - verificai-network

  # Redis Cache
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    networks:
      - verificai-network

  # Backend API
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://verificai:verificai123@postgres:5432/verificai
      - REDIS_URL=redis://redis:6379
      - ENVIRONMENT=development
    depends_on:
      - postgres
      - redis
    volumes:
      - ./backend:/app
      - ./backend/static/uploads:/app/static/uploads
    networks:
      - verificai-network
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

  # Frontend
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:8000
      - REACT_APP_WS_URL=ws://localhost:8000
    volumes:
      - ./frontend:/app
      - /app/node_modules
    depends_on:
      - backend
    networks:
      - verificai-network
    command: npm run dev

  # Celery Worker
  celery:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      - DATABASE_URL=postgresql://verificai:verificai123@postgres:5432/verificai
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis
    volumes:
      - ./backend:/app
      - ./backend/static/uploads:/app/static/uploads
    networks:
      - verificai-network
    command: celery -A app.core.workers.celery_app worker --loglevel=info

  # Celery Beat (for scheduled tasks)
  celery-beat:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      - DATABASE_URL=postgresql://verificai:verificai123@postgres:5432/verificai
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis
    volumes:
      - ./backend:/app
    networks:
      - verificai-network
    command: celery -A app.core.workers.celery_app beat --loglevel=info

volumes:
  postgres_data:

networks:
  verificai-network:
    driver: bridge
```

### 9.2 Production Deployment

#### 9.2.1 Kubernetes Deployment

```yaml
# infrastructure/kubernetes/backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: verificai-backend
  labels:
    app: verificai-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: verificai-backend
  template:
    metadata:
      labels:
        app: verificai-backend
    spec:
      containers:
      - name: backend
        image: verificai/backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: verificai-secrets
              key: database-url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: verificai-secrets
              key: redis-url
        - name: ENVIRONMENT
          value: "production"
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5

---
apiVersion: v1
kind: Service
metadata:
  name: verificai-backend-service
spec:
  selector:
    app: verificai-backend
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: LoadBalancer
```

```yaml
# infrastructure/kubernetes/frontend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: verificai-frontend
  labels:
    app: verificai-frontend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: verificai-frontend
  template:
    metadata:
      labels:
        app: verificai-frontend
    spec:
      containers:
      - name: frontend
        image: verificai/frontend:latest
        ports:
        - containerPort: 3000
        env:
        - name: REACT_APP_API_URL
          value: "https://api.verificai.example.com"
        - name: REACT_APP_WS_URL
          value: "wss://api.verificai.example.com"
        resources:
          requests:
            memory: "256Mi"
            cpu: "125m"
          limits:
            memory: "512Mi"
            cpu: "250m"

---
apiVersion: v1
kind: Service
metadata:
  name: verificai-frontend-service
spec:
  selector:
    app: verificai-frontend
  ports:
    - protocol: TCP
      port: 80
      targetPort: 3000
  type: LoadBalancer
```

### 9.3 CI/CD Pipeline

#### 9.3.1 GitHub Actions Configuration

```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

env:
  NODE_VERSION: '18'
  PYTHON_VERSION: '3.11'

jobs:
  test:
    runs-on: ubuntu-latest

    strategy:
      matrix:
        node-version: [18.x, 20.x]
        python-version: [3.11]

    steps:
    - uses: actions/checkout@v4

    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: ${{ matrix.node-version }}
        cache: 'npm'
        cache-dependency-path: frontend/package-lock.json

    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
        cache: 'pip'
        cache-dependency-path: backend/requirements.txt

    - name: Install frontend dependencies
      working-directory: ./frontend
      run: npm ci

    - name: Install backend dependencies
      working-directory: ./backend
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt

    - name: Run frontend tests
      working-directory: ./frontend
      run: |
        npm run type-check
        npm run lint
        npm run test:coverage

    - name: Run backend tests
      working-directory: ./backend
      run: |
        pytest tests/ --cov=app --cov-report=xml

    - name: Build frontend
      working-directory: ./frontend
      run: npm run build

    - name: Upload coverage reports
      if: matrix.node-version == '20.x'
      uses: codecov/codecov-action@v3
      with:
        files: ./frontend/coverage/lcov.info,./backend/coverage.xml
        flags: frontend,backend
        name: code-coverage

  security:
    runs-on: ubuntu-latest
    if: github.event_name == 'pull_request'

    steps:
    - uses: actions/checkout@v4

    - name: Run security audit
      working-directory: ./frontend
      run: npm audit --audit-level=moderate

    - name: Run backend security scan
      working-directory: ./backend
      run: |
        pip install bandit safety
        bandit -r app/
        safety check

  build-and-deploy:
    runs-on: ubuntu-latest
    needs: [test, security]
    if: github.ref == 'refs/heads/main' || github.ref == 'refs/heads/develop'

    steps:
    - uses: actions/checkout@v4

    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3

    - name: Login to Container Registry
      uses: docker/login-action@v3
      with:
        registry: ghcr.io
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}

    - name: Build and push backend
      uses: docker/build-push-action@v5
      with:
        context: ./backend
        push: true
        tags: ghcr.io/${{ github.repository }}/backend:${{ github.sha }}
        cache-from: type=gha
        cache-to: type=gha,mode=max

    - name: Build and push frontend
      uses: docker/build-push-action@v5
      with:
        context: ./frontend
        push: true
        tags: ghcr.io/${{ github.repository }}/frontend:${{ github.sha }}
        cache-from: type=gha
        cache-to: type=gha,mode=max

    - name: Deploy to staging
      if: github.ref == 'refs/heads/develop'
      uses: appleboy/ssh-action@v1.0.0
      with:
        host: ${{ secrets.STAGING_HOST }}
        username: ${{ secrets.STAGING_USER }}
        key: ${{ secrets.STAGING_SSH_KEY }}
        script: |
          cd /opt/verificai
          docker-compose pull
          docker-compose up -d

    - name: Deploy to production
      if: github.ref == 'refs/heads/main'
      uses: appleboy/ssh-action@v1.0.0
      with:
        host: ${{ secrets.PRODUCTION_HOST }}
        username: ${{ secrets.PRODUCTION_USER }}
        key: ${{ secrets.PRODUCTION_SSH_KEY }}
        script: |
          cd /opt/verificai
          docker-compose pull
          docker-compose up -d
```

---

## 10. Error Handling Strategy

### 10.1 Error Categories and Handling

#### 10.1.1 System Errors

```python
# backend/app/core/errors/base.py
from typing import Optional, Dict, Any
from enum import Enum

class ErrorType(Enum):
    VALIDATION_ERROR = "validation_error"
    AUTHENTICATION_ERROR = "authentication_error"
    AUTHORIZATION_ERROR = "authorization_error"
    NOT_FOUND_ERROR = "not_found_error"
    CONFLICT_ERROR = "conflict_error"
    RATE_LIMIT_ERROR = "rate_limit_error"
    EXTERNAL_SERVICE_ERROR = "external_service_error"
    DATABASE_ERROR = "database_error"
    FILE_PROCESSING_ERROR = "file_processing_error"
    LLM_ERROR = "llm_error"
    INTERNAL_ERROR = "internal_error"

class BaseError(Exception):
    def __init__(
        self,
        message: str,
        error_type: ErrorType,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_type = error_type
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

class ValidationError(BaseError):
    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(
            message=message,
            error_type=ErrorType.VALIDATION_ERROR,
            status_code=422,
            details={"field": field} if field else {}
        )

class AuthenticationError(BaseError):
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            error_type=ErrorType.AUTHENTICATION_ERROR,
            status_code=401
        )

class AuthorizationError(BaseError):
    def __init__(self, message: str = "Authorization failed"):
        super().__init__(
            message=message,
            error_type=ErrorType.AUTHORIZATION_ERROR,
            status_code=403
        )

class NotFoundError(BaseError):
    def __init__(self, resource_type: str, resource_id: str):
        super().__init__(
            message=f"{resource_type} with id '{resource_id}' not found",
            error_type=ErrorType.NOT_FOUND_ERROR,
            status_code=404,
            details={"resource_type": resource_type, "resource_id": resource_id}
        )

class ExternalServiceError(BaseError):
    def __init__(self, service: str, message: str):
        super().__init__(
            message=f"External service '{service}' error: {message}",
            error_type=ErrorType.EXTERNAL_SERVICE_ERROR,
            status_code=502,
            details={"service": service}
        )

class LLMError(BaseError):
    def __init__(self, provider: str, message: str):
        super().__init__(
            message=f"LLM provider '{provider}' error: {message}",
            error_type=ErrorType.LLM_ERROR,
            status_code=502,
            details={"provider": provider}
        )
```

#### 10.1.2 Error Middleware

```python
# backend/app/middleware/error_handler.py
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
import logging
import traceback
from typing import Dict, Any
from ..core.errors.base import BaseError, ErrorType

logger = logging.getLogger(__name__)

class ErrorHandler:
    @staticmethod
    def create_error_response(error: BaseError) -> Dict[str, Any]:
        """Create standardized error response"""
        return {
            "error": {
                "type": error.error_type.value,
                "message": error.message,
                "details": error.details
            },
            "success": False
        }

    @staticmethod
    async def handle_base_error(request: Request, error: BaseError) -> JSONResponse:
        """Handle application-specific errors"""
        logger.error(f"Application error: {error.error_type.value} - {error.message}")

        return JSONResponse(
            status_code=error.status_code,
            content=ErrorHandler.create_error_response(error)
        )

    @staticmethod
    async def handle_validation_error(request: Request, error: RequestValidationError) -> JSONResponse:
        """Handle FastAPI validation errors"""
        logger.error(f"Validation error: {error.errors()}")

        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "type": ErrorType.VALIDATION_ERROR.value,
                    "message": "Invalid request data",
                    "details": {"validation_errors": error.errors()}
                },
                "success": False
            }
        )

    @staticmethod
    async def handle_http_exception(request: Request, error: HTTPException) -> JSONResponse:
        """Handle HTTP exceptions"""
        logger.error(f"HTTP exception: {error.status_code} - {error.detail}")

        return JSONResponse(
            status_code=error.status_code,
            content={
                "error": {
                    "type": "http_error",
                    "message": error.detail,
                    "details": {}
                },
                "success": False
            }
        )

    @staticmethod
    async def handle_unexpected_error(request: Request, error: Exception) -> JSONResponse:
        """Handle unexpected errors"""
        logger.error(f"Unexpected error: {str(error)}")
        logger.error(traceback.format_exc())

        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "type": ErrorType.INTERNAL_ERROR.value,
                    "message": "An unexpected error occurred",
                    "details": {}
                },
                "success": False
            }
        )
```

### 10.2 Retry and Fallback Mechanisms

```python
# backend/app/core/utils/retry.py
import asyncio
import random
from typing import TypeVar, Callable, Any, Optional
from functools import wraps
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')

class RetryConfig:
    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 30.0,
        exponential_base: float = 2.0,
        jitter: bool = True
    ):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter

def retry_with_fallback(
    config: RetryConfig = None,
    fallback_function: Optional[Callable] = None
):
    """Decorator for retry with fallback functionality"""
    if config is None:
        config = RetryConfig()

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> T:
            last_exception = None

            for attempt in range(config.max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")

                    if attempt < config.max_attempts - 1:
                        delay = _calculate_delay(config, attempt)
                        await asyncio.sleep(delay)
                    else:
                        logger.error(f"All {config.max_attempts} attempts failed")

            # Try fallback function if available
            if fallback_function:
                try:
                    logger.info("Attempting fallback function")
                    return await fallback_function(*args, **kwargs)
                except Exception as fallback_error:
                    logger.error(f"Fallback function failed: {str(fallback_error)}")

            # Re-raise the last exception
            raise last_exception

        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> T:
            last_exception = None

            for attempt in range(config.max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")

                    if attempt < config.max_attempts - 1:
                        delay = _calculate_delay(config, attempt)
                        asyncio.sleep(delay)
                    else:
                        logger.error(f"All {config.max_attempts} attempts failed")

            # Try fallback function if available
            if fallback_function:
                try:
                    logger.info("Attempting fallback function")
                    return fallback_function(*args, **kwargs)
                except Exception as fallback_error:
                    logger.error(f"Fallback function failed: {str(fallback_error)}")

            # Re-raise the last exception
            raise last_exception

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator

def _calculate_delay(config: RetryConfig, attempt: int) -> float:
    """Calculate delay with exponential backoff and jitter"""
    delay = config.base_delay * (config.exponential_base ** attempt)
    delay = min(delay, config.max_delay)

    if config.jitter:
        delay = delay * (0.5 + random.random() * 0.5)

    return delay
```

### 10.3 Circuit Breaker Pattern

```python
# backend/app/core/utils/circuit_breaker.py
import asyncio
import time
from enum import Enum
from typing import Callable, TypeVar, Optional
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = Exception
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception

        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
        self.lock = asyncio.Lock()

    async def call(self, func: Callable[..., T], *args, **kwargs) -> T:
        """Execute function with circuit breaker protection"""
        async with self.lock:
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self.state = CircuitState.HALF_OPEN
                    logger.info("Circuit breaker moving to HALF_OPEN state")
                else:
                    raise self.expected_exception("Circuit breaker is OPEN")

        try:
            result = await func(*args, **kwargs)
            await self._on_success()
            return result
        except self.expected_exception as e:
            await self._on_failure()
            raise e

    def _should_attempt_reset(self) -> bool:
        """Check if circuit breaker should attempt reset"""
        if self.last_failure_time is None:
            return True

        return (time.time() - self.last_failure_time) >= self.recovery_timeout

    async def _on_success(self):
        """Handle successful execution"""
        async with self.lock:
            self.failure_count = 0
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.CLOSED
                logger.info("Circuit breaker reset to CLOSED state")

    async def _on_failure(self):
        """Handle failed execution"""
        async with self.lock:
            self.failure_count += 1
            self.last_failure_time = time.time()

            if (self.state == CircuitState.CLOSED and
                self.failure_count >= self.failure_threshold):
                self.state = CircuitState.OPEN
                logger.warning(f"Circuit breaker opened after {self.failure_count} failures")
            elif self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.OPEN
                logger.warning("Circuit breaker re-opened from HALF_OPEN state")
```

---

## 11. Security Requirements

### 11.1 Authentication and Authorization

#### 11.1.1 JWT Implementation

```python
# backend/app/core/security/jwt.py
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
import os

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
```

#### 11.1.2 Authorization Middleware

```python
# backend/app/middleware/auth.py
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from ..core.security.jwt import verify_token
from ..repositories.user_repository import UserRepository
from ..database.connection import get_db
from sqlalchemy.orm import Session

security = HTTPBearer()

async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get current authenticated user"""
    token = credentials.credentials
    payload = verify_token(token)

    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

    user_repository = UserRepository(db)
    user = user_repository.get_by_id(user_id)

    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    if not user.is_active:
        raise HTTPException(status_code=401, detail="Inactive user")

    return user

async def get_current_active_user(current_user = Depends(get_current_user)):
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def require_role(required_role: str):
    """Role-based access control decorator"""
    def role_checker(current_user = Depends(get_current_active_user)):
        if current_user.role != required_role:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return role_checker
```

### 11.2 Input Validation and Sanitization

#### 11.2.1 File Upload Security

```python
# backend/app/core/security/file_security.py
import os
import magic
from typing import List, Set
from pathlib import Path

class FileSecurity:
    ALLOWED_MIME_TYPES: Set[str] = {
        'text/plain',
        'text/x-python',
        'text/x-java-source',
        'text/javascript',
        'application/javascript',
        'text/typescript',
        'application/x-typescript',
        'text/x-csrc',
        'text/x-c++src',
        'application/json',
        'text/markdown',
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    }

    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    DANGEROUS_EXTENSIONS: Set[str] = {
        '.exe', '.bat', '.cmd', '.sh', '.php', '.asp', '.aspx', '.jsp'
    }

    @classmethod
    def validate_file(cls, file_path: str) -> List[str]:
        """Validate uploaded file for security"""
        errors = []

        # Check file size
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            if file_size > cls.MAX_FILE_SIZE:
                errors.append(f"File size exceeds maximum limit of {cls.MAX_FILE_SIZE} bytes")

        # Check file extension
        path = Path(file_path)
        if path.suffix.lower() in cls.DANGEROUS_EXTENSIONS:
            errors.append(f"Dangerous file extension: {path.suffix}")

        # Check MIME type
        try:
            mime_type = magic.from_file(file_path, mime=True)
            if mime_type not in cls.ALLOWED_MIME_TYPES:
                errors.append(f"Unsupported file type: {mime_type}")
        except Exception as e:
            errors.append(f"Could not determine file type: {str(e)}")

        # Check for potential malicious content
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                if cls._contains_malicious_content(content):
                    errors.append("File contains potentially malicious content")
        except Exception:
            # If we can't read as text, it might be binary - already handled by MIME type
            pass

        return errors

    @classmethod
    def _contains_malicious_content(cls, content: str) -> bool:
        """Check for potentially malicious content patterns"""
        malicious_patterns = [
            'eval(',
            'exec(',
            'system(',
            'subprocess.',
            'os.system',
            '__import__',
            'base64.decode',
            'pickle.loads',
            'marshal.loads'
        ]

        content_lower = content.lower()
        for pattern in malicious_patterns:
            if pattern in content_lower:
                return True

        return False

    @classmethod
    def sanitize_filename(cls, filename: str) -> str:
        """Sanitize filename to prevent path traversal"""
        # Remove path separators
        filename = filename.replace('/', '_').replace('\\', '_')

        # Remove potentially dangerous characters
        dangerous_chars = ['..', ':', '*', '?', '"', '<', '>', '|']
        for char in dangerous_chars:
            filename = filename.replace(char, '_')

        # Limit filename length
        max_length = 255
        if len(filename) > max_length:
            name, ext = os.path.splitext(filename)
            filename = name[:max_length - len(ext)] + ext

        return filename
```

#### 11.2.2 XSS Prevention

```python
# backend/app/core/security/xss_prevention.py
import re
import html
from typing import Optional
import bleach

class XSSPrevention:
    ALLOWED_TAGS = [
        'p', 'br', 'strong', 'em', 'u', 'code', 'pre', 'blockquote',
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'ul', 'ol', 'li', 'dl', 'dt', 'dd',
        'table', 'thead', 'tbody', 'tr', 'th', 'td',
        'a', 'img', 'div', 'span'
    ]

    ALLOWED_ATTRIBUTES = {
        'a': ['href', 'title'],
        'img': ['src', 'alt', 'title'],
        'code': ['class'],
        'pre': ['class'],
        'div': ['class'],
        'span': ['class']
    }

    @classmethod
    def sanitize_html(cls, html_content: str) -> str:
        """Sanitize HTML content to prevent XSS"""
        return bleach.clean(
            html_content,
            tags=cls.ALLOWED_TAGS,
            attributes=cls.ALLOWED_ATTRIBUTES,
            strip=True
        )

    @classmethod
    def sanitize_text(cls, text: str) -> str:
        """Sanitize plain text content"""
        # HTML escape
        sanitized = html.escape(text)

        # Remove potentially dangerous Unicode characters
        sanitized = cls._remove_dangerous_unicode(sanitized)

        # Remove control characters except basic whitespace
        sanitized = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', sanitized)

        return sanitized

    @classmethod
    def _remove_dangerous_unicode(cls, text: str) -> str:
        """Remove potentially dangerous Unicode characters"""
        dangerous_ranges = [
            (0x2028, 0x2029),  # Line separator and paragraph separator
            (0x200B, 0x200D),  # Zero-width characters
            (0x2060, 0x206F),  # Invisible characters
        ]

        result = []
        for char in text:
            code_point = ord(char)
            dangerous = False

            for start, end in dangerous_ranges:
                if start <= code_point <= end:
                    dangerous = True
                    break

            if not dangerous:
                result.append(char)

        return ''.join(result)
```

### 11.3 Security Headers

```python
# backend/app/middleware/security_headers.py
from fastapi import Request, Response
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware

class SecurityHeadersMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                headers = dict(message.get("headers", []))

                # Add security headers
                headers[b"content-security-policy"] = b"default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' wss: https:; frame-ancestors 'none';"
                headers[b"x-content-type-options"] = b"nosniff"
                headers[b"x-frame-options"] = b"DENY"
                headers[b"x-xss-protection"] = b"1; mode=block"
                headers[b"strict-transport-security"] = b"max-age=31536000; includeSubDomains"
                headers[b"referrer-policy"] = b"strict-origin-when-cross-origin"
                headers[b"permissions-policy"] = b"camera=(), microphone=(), geolocation=()"

                message["headers"] = list(headers.items())

            await send(message)

        await self.app(scope, receive, send_wrapper)

def create_cors_middleware():
    """Create CORS middleware configuration"""
    return CORSMiddleware(
        allow_origins=[
            "http://localhost:3000",
            "https://localhost:3000",
            "https://verificai.example.com"
        ],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=[
            "Authorization",
            "Content-Type",
            "X-Requested-With",
            "X-CSRF-Token"
        ],
        max_age=600
    )
```

---

## 12. Performance Optimization

### 12.1 Frontend Performance

#### 12.1.1 Code Splitting and Lazy Loading

```typescript
// frontend/src/router.tsx
import { createBrowserRouter, createRoutesFromElements, Route } from 'react-router-dom';
import { Suspense, lazy } from 'react';
import MainLayout from './components/layout/MainLayout';
import LoadingSpinner from './components/common/Feedback/LoadingSpinner';

// Lazy loading for code splitting
const DashboardPage = lazy(() => import('./pages/DashboardPage'));
const CodeUploadPage = lazy(() => import('./pages/CodeUploadPage'));
const PromptConfigPage = lazy(() => import('./pages/PromptConfigPage'));
const GeneralAnalysisPage = lazy(() => import('./pages/GeneralAnalysisPage'));
const ArchitecturalAnalysisPage = lazy(() => import('./pages/ArchitecturalAnalysisPage'));
const BusinessAnalysisPage = lazy(() => import('./pages/BusinessAnalysisPage'));
const SettingsPage = lazy(() => import('./pages/SettingsPage'));

const router = createBrowserRouter(
  createRoutesFromElements(
    <Route path="/" element={<MainLayout />}>
      <Route
        index
        element={
          <Suspense fallback={<LoadingSpinner />}>
            <DashboardPage />
          </Suspense>
        }
      />
      <Route
        path="upload"
        element={
          <Suspense fallback={<LoadingSpinner />}>
            <CodeUploadPage />
          </Suspense>
        }
      />
      <Route
        path="prompts"
        element={
          <Suspense fallback={<LoadingSpinner />}>
            <PromptConfigPage />
          </Suspense>
        }
      />
      <Route
        path="analysis/general"
        element={
          <Suspense fallback={<LoadingSpinner />}>
            <GeneralAnalysisPage />
          </Suspense>
        }
      />
      <Route
        path="analysis/architectural"
        element={
          <Suspense fallback={<LoadingSpinner />}>
            <ArchitecturalAnalysisPage />
          </Suspense>
        }
      />
      <Route
        path="analysis/business"
        element={
          <Suspense fallback={<LoadingSpinner />}>
            <BusinessAnalysisPage />
          </Suspense>
        }
      />
      <Route
        path="settings"
        element={
          <Suspense fallback={<LoadingSpinner />}>
            <SettingsPage />
          </Suspense>
        }
      />
    </Route>
  )
);

export default router;
```

#### 12.1.2 Virtual Scrolling for Large Lists

```typescript
// frontend/src/components/features/Analysis/ResultsTable.tsx
import { FixedSizeList as List } from 'react-window';
import { useMemo } from 'react';
import type { AnalysisResult } from '../../types/analysis';

interface ResultsTableProps {
  results: AnalysisResult[];
  onSelectResult: (result: AnalysisResult) => void;
}

const ResultsTable: React.FC<ResultsTableProps> = ({ results, onSelectResult }) => {
  const sortedResults = useMemo(() => {
    return [...results].sort((a, b) => {
      // Sort by score descending, then by file name
      if (a.score && b.score) {
        return b.score - a.score;
      }
      if (a.score) return -1;
      if (b.score) return 1;
      return a.fileName?.localeCompare(b.fileName || '') || 0;
    });
  }, [results]);

  const Row = ({ index, style }: { index: number; style: React.CSSProperties }) => {
    const result = sortedResults[index];

    return (
      <div
        style={style}
        className={`border-b border-gray-200 hover:bg-gray-50 cursor-pointer ${
          index % 2 === 0 ? 'bg-white' : 'bg-gray-50'
        }`}
        onClick={() => onSelectResult(result)}
      >
        <div className="p-4">
          <div className="flex justify-between items-start">
            <div className="flex-1">
              <h3 className="font-medium text-gray-900">
                {result.fileName || 'Unnamed File'}
              </h3>
              <p className="text-sm text-gray-500 mt-1">
                {result.analysisType} Analysis
              </p>
            </div>
            <div className="flex items-center space-x-2">
              {result.score && (
                <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                  result.score >= 8 ? 'bg-green-100 text-green-800' :
                  result.score >= 6 ? 'bg-yellow-100 text-yellow-800' :
                  'bg-red-100 text-red-800'
                }`}>
                  {result.score.toFixed(1)}
                </span>
              )}
              <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                result.status === 'completed' ? 'bg-green-100 text-green-800' :
                result.status === 'processing' ? 'bg-blue-100 text-blue-800' :
                result.status === 'failed' ? 'bg-red-100 text-red-800' :
                'bg-gray-100 text-gray-800'
              }`}>
                {result.status}
              </span>
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="bg-white rounded-lg shadow border border-gray-200">
      <div className="px-6 py-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900">
          Analysis Results ({results.length})
        </h2>
      </div>

      {results.length === 0 ? (
        <div className="p-8 text-center">
          <p className="text-gray-500">No analysis results available</p>
        </div>
      ) : (
        <List
          height={600}
          itemCount={sortedResults.length}
          itemSize={80}
          itemData={sortedResults}
          className="divide-y divide-gray-200"
        >
          {Row}
        </List>
      )}
    </div>
  );
};

export default ResultsTable;
```

#### 12.1.3 Image and Asset Optimization

```typescript
// frontend/src/utils/imageOptimization.ts
export class ImageOptimizer {
  private static readonly MAX_WIDTH = 800;
  private static readonly MAX_HEIGHT = 600;
  private static readonly QUALITY = 0.8;
  private static readonly MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB

  static async optimizeImage(file: File): Promise<string> {
    return new Promise((resolve, reject) => {
      const img = new Image();
      const reader = new FileReader();

      reader.onload = (e) => {
        img.onload = () => {
          const canvas = document.createElement('canvas');
          const ctx = canvas.getContext('2d');

          if (!ctx) {
            reject(new Error('Canvas context not available'));
            return;
          }

          // Calculate new dimensions
          let { width, height } = img;

          if (width > height) {
            if (width > this.MAX_WIDTH) {
              height = (height * this.MAX_WIDTH) / width;
              width = this.MAX_WIDTH;
            }
          } else {
            if (height > this.MAX_HEIGHT) {
              width = (width * this.MAX_HEIGHT) / height;
              height = this.MAX_HEIGHT;
            }
          }

          canvas.width = width;
          canvas.height = height;

          // Draw image on canvas
          ctx.drawImage(img, 0, 0, width, height);

          // Convert to blob with compression
          canvas.toBlob(
            (blob) => {
              if (!blob) {
                reject(new Error('Failed to create blob'));
                return;
              }

              // Check if optimized image is still too large
              if (blob.size > this.MAX_FILE_SIZE) {
                // Further reduce quality
                const quality = this.MAX_FILE_SIZE / blob.size;
                canvas.toBlob(
                  (finalBlob) => {
                    if (!finalBlob) {
                      reject(new Error('Failed to create final blob'));
                      return;
                    }
                    resolve(URL.createObjectURL(finalBlob));
                  },
                  'image/jpeg',
                  quality * 0.8
                );
              } else {
                resolve(URL.createObjectURL(blob));
              }
            },
            'image/jpeg',
            this.QUALITY
          );
        };

        img.onerror = () => {
          reject(new Error('Failed to load image'));
        };

        img.src = e.target?.result as string;
      };

      reader.onerror = () => {
        reject(new Error('Failed to read file'));
      };

      reader.readAsDataURL(file);
    });
  }

  static async getFileDimensions(file: File): Promise<{ width: number; height: number }> {
    return new Promise((resolve, reject) => {
      const img = new Image();
      const reader = new FileReader();

      reader.onload = (e) => {
        img.onload = () => {
          resolve({
            width: img.naturalWidth,
            height: img.naturalHeight
          });
        };

        img.onerror = () => {
          reject(new Error('Failed to load image'));
        };

        img.src = e.target?.result as string;
      };

      reader.onerror = () => {
        reject(new Error('Failed to read file'));
      };

      reader.readAsDataURL(file);
    });
  }
}
```

### 12.2 Backend Performance

#### 12.2.1 Database Optimization

```python
# backend/app/database/optimization.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Index, text
import os

class DatabaseOptimizer:
    @staticmethod
    def create_optimized_engine(database_url: str):
        """Create optimized database engine"""
        return create_engine(
            database_url,
            poolclass=QueuePool,
            pool_size=20,
            max_overflow=30,
            pool_pre_ping=True,
            pool_recycle=300,
            pool_timeout=30,
            echo=False,  # Set to True for debugging
            execution_options={
                "isolation_level": "READ COMMITTED",
                "autocommit": False
            }
        )

    @staticmethod
    def create_optimized_indexes():
        """Create optimized database indexes"""
        return [
            # Composite indexes for common query patterns
            Index('idx_analysis_sessions_user_created',
                  text("(user_id, created_at DESC)")),
            Index('idx_analysis_results_session_type_status',
                  text("(analysis_session_id, analysis_type, status)")),
            Index('idx_file_uploads_session_status',
                  text("(analysis_session_id, upload_status)")),

            # Partial indexes for active data
            Index('idx_active_sessions',
                  text("(status) WHERE status IN ('created', 'processing')")),
            Index('idx_recent_results',
                  text("(created_at) WHERE created_at > NOW() - INTERVAL '7 days'")),

            # Text search indexes
            Index('idx_configurations_search',
                  text("to_tsvector('english', prompt_content)"),
                  postgresql_using='gin')
        ]

    @staticmethod
    def optimize_query(query, limit=None, offset=None):
        """Apply common query optimizations"""
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)

        return query

    @staticmethod
    def get_paginated_query(query, page=1, per_page=20):
        """Get paginated query with count"""
        total = query.count()
        items = query.offset((page - 1) * per_page).limit(per_page).all()

        return {
            'items': items,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page
        }
```

#### 12.2.2 Caching Strategy

```python
# backend/app/core/services/cache_service.py
import json
import pickle
from typing import Any, Optional, Union
from datetime import datetime, timedelta
import redis
from functools import wraps
import logging

logger = logging.getLogger(__name__)

class CacheService:
    def __init__(self, redis_url: str):
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
        self.default_ttl = 3600  # 1 hour

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            value = self.redis_client.get(key)
            if value is None:
                return None

            # Try to parse as JSON first, then as pickle
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                try:
                    return pickle.loads(value.encode('latin1'))
                except:
                    return value
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        use_pickle: bool = False
    ) -> bool:
        """Set value in cache"""
        try:
            if ttl is None:
                ttl = self.default_ttl

            if use_pickle:
                serialized_value = pickle.dumps(value)
            else:
                try:
                    serialized_value = json.dumps(value, default=str)
                except TypeError:
                    serialized_value = pickle.dumps(value)
                    use_pickle = True

            return self.redis_client.setex(key, ttl, serialized_value)
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            return bool(self.redis_client.exists(key))
        except Exception as e:
            logger.error(f"Cache exists error: {e}")
            return False

    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern"""
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache clear pattern error: {e}")
            return 0

    def cache_result(self, ttl: int = None, key_prefix: str = ""):
        """Decorator for caching function results"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Create cache key
                cache_key = f"{key_prefix}{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"

                # Try to get from cache
                cached_result = await self.get(cache_key)
                if cached_result is not None:
                    return cached_result

                # Execute function
                result = await func(*args, **kwargs)

                # Cache result
                await self.set(cache_key, result, ttl)

                return result
            return wrapper
        return decorator

# Usage example
cache_service = CacheService(os.getenv("REDIS_URL"))

@cache_service.cache_result(ttl=1800, key_prefix="analysis:")
async def get_analysis_results(session_id: str):
    # Database query logic
    pass
```

#### 12.2.3 Connection Pooling

```python
# backend/app/database/connection_pool.py
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import SQLAlchemyError
import contextlib
import logging
import time
import os

logger = logging.getLogger(__name__)

class ConnectionPoolManager:
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.engine = None
        self.pool_stats = {
            'total_connections': 0,
            'active_connections': 0,
            'idle_connections': 0,
            'failed_connections': 0,
            'avg_connection_time': 0
        }
        self._setup_pool()

    def _setup_pool(self):
        """Setup connection pool with optimized settings"""
        self.engine = create_engine(
            self.database_url,
            poolclass=QueuePool,
            pool_size=20,           # Number of permanent connections
            max_overflow=30,        # Additional connections when pool is full
            pool_pre_ping=True,     # Check connection before use
            pool_recycle=300,       # Recycle connections after 5 minutes
            pool_timeout=30,        # Wait time for connection
            echo=False,             # SQL logging
            connect_args={
                'connect_timeout': 10,
                'application_name': 'verificai-backend',
                'options': '-c timezone=utc'
            }
        )

    @contextlib.contextmanager
    def get_connection(self):
        """Get connection from pool with timing and error handling"""
        start_time = time.time()
        connection = None

        try:
            connection = self.engine.connect()
            connection_time = time.time() - start_time

            # Update pool statistics
            self.pool_stats['total_connections'] += 1
            self.pool_stats['active_connections'] += 1

            # Update average connection time
            if self.pool_stats['avg_connection_time'] == 0:
                self.pool_stats['avg_connection_time'] = connection_time
            else:
                self.pool_stats['avg_connection_time'] = (
                    self.pool_stats['avg_connection_time'] * 0.9 + connection_time * 0.1
                )

            yield connection

        except SQLAlchemyError as e:
            self.pool_stats['failed_connections'] += 1
            logger.error(f"Connection pool error: {e}")
            raise
        finally:
            if connection:
                connection.close()
                self.pool_stats['active_connections'] -= 1
                self.pool_stats['idle_connections'] += 1

    def get_pool_stats(self) -> dict:
        """Get current pool statistics"""
        pool = self.engine.pool
        return {
            **self.pool_stats,
            'pool_size': pool.size(),
            'checked_in': pool.checkedin(),
            'checked_out': pool.checkedout(),
            'overflow': pool.overflow(),
            'invalidated': pool.invalidated()
        }

    def health_check(self) -> bool:
        """Check if connection pool is healthy"""
        try:
            with self.get_connection() as conn:
                conn.execute("SELECT 1")
                return True
        except Exception as e:
            logger.error(f"Pool health check failed: {e}")
            return False

    def close_pool(self):
        """Close all connections in pool"""
        if self.engine:
            self.engine.dispose()
            logger.info("Connection pool closed")

# Global instance
pool_manager = ConnectionPoolManager(os.getenv("DATABASE_URL"))
```

---

## 13. Monitoring and Observability

### 13.1 Logging Strategy

#### 13.1.1 Structured Logging

```python
# backend/app/core/logging_config.py
import logging
import logging.handlers
import json
import sys
from datetime import datetime
from typing import Dict, Any, Optional
from contextlib import contextmanager
import os

class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured JSON logging"""

    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }

        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': self.formatException(record.exc_info)
            }

        # Add custom fields
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        if hasattr(record, 'session_id'):
            log_entry['session_id'] = record.session_id
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
        if hasattr(record, 'extra_data'):
            log_entry['extra_data'] = record.extra_data

        return json.dumps(log_entry)

def setup_logging():
    """Setup structured logging for the application"""
    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(StructuredFormatter())
    root_logger.addHandler(console_handler)

    # File handler with rotation
    if os.getenv('ENVIRONMENT') == 'production':
        file_handler = logging.handlers.RotatingFileHandler(
            '/var/log/verificai/app.log',
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(StructuredFormatter())
        root_logger.addHandler(file_handler)

    # Set specific loggers
    logging.getLogger('uvicorn.access').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

    return root_logger

class LoggerMixin:
    """Mixin class for adding logging to classes"""

    @property
    def logger(self):
        if not hasattr(self, '_logger'):
            self._logger = logging.getLogger(self.__class__.__name__)
        return self._logger

    def log_with_context(
        self,
        level: str,
        message: str,
        extra: Optional[Dict[str, Any]] = None
    ):
        """Log message with additional context"""
        log_method = getattr(self.logger, level.lower(), self.logger.info)

        kwargs = {'extra': extra} if extra else {}
        log_method(message, **kwargs)

@contextmanager
def log_operation(operation_name: str, logger: logging.Logger, **context):
    """Context manager for logging operation duration and results"""
    start_time = datetime.utcnow()
    logger.info(f"Starting operation: {operation_name}", extra=context)

    try:
        yield
        duration = (datetime.utcnow() - start_time).total_seconds()
        logger.info(
            f"Completed operation: {operation_name}",
            extra={
                **context,
                'duration_seconds': duration,
                'status': 'success'
            }
        )
    except Exception as e:
        duration = (datetime.utcnow() - start_time).total_seconds()
        logger.error(
            f"Failed operation: {operation_name}",
            extra={
                **context,
                'duration_seconds': duration,
                'status': 'error',
                'error': str(e)
            }
        )
        raise
```

#### 13.1.2 Request Logging Middleware

```python
# backend/app/middleware/request_logging.py
from fastapi import Request, Response
from fastapi.middleware import Middleware
import time
import uuid
import logging

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive)

        # Generate request ID
        request_id = str(uuid.uuid4())
        scope['request_id'] = request_id

        # Extract user info if available
        user_id = getattr(request.state, 'user_id', None)
        session_id = getattr(request.state, 'session_id', None)

        # Log request start
        start_time = time.time()
        logger.info(
            "Incoming request",
            extra={
                'request_id': request_id,
                'method': request.method,
                'url': str(request.url),
                'user_agent': request.headers.get('user-agent'),
                'user_id': user_id,
                'session_id': session_id
            }
        )

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                # Calculate request duration
                duration = time.time() - start_time
                status_code = message.get("status", 500)

                # Log request completion
                log_level = "error" if status_code >= 500 else "warning" if status_code >= 400 else "info"
                getattr(logger, log_level)(
                    "Request completed",
                    extra={
                        'request_id': request_id,
                        'method': request.method,
                        'url': str(request.url),
                        'status_code': status_code,
                        'duration_seconds': duration,
                        'user_id': user_id,
                        'session_id': session_id
                    }
                )

                # Add request ID to response headers
                headers = dict(message.get("headers", []))
                headers[b"X-Request-ID"] = request_id.encode()
                message["headers"] = list(headers.items())

            await send(message)

        await self.app(scope, receive, send_wrapper)
```

### 13.2 Metrics and Monitoring

#### 13.2.1 Custom Metrics

```python
# backend/app/core/metrics.py
import time
import threading
from collections import defaultdict, deque
from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

@dataclass
class MetricPoint:
    timestamp: datetime
    value: float
    tags: Dict[str, str]

class MetricsCollector:
    def __init__(self, max_points: int = 1000):
        self.max_points = max_points
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_points))
        self.counters: Dict[str, int] = defaultdict(int)
        self.lock = threading.Lock()

    def record_gauge(
        self,
        name: str,
        value: float,
        tags: Dict[str, str] = None
    ):
        """Record a gauge metric (current value)"""
        with self.lock:
            point = MetricPoint(
                timestamp=datetime.utcnow(),
                value=value,
                tags=tags or {}
            )
            self.metrics[name].append(point)

    def increment_counter(
        self,
        name: str,
        value: int = 1,
        tags: Dict[str, str] = None
    ):
        """Increment a counter metric"""
        with self.lock:
            key = f"{name}:{self._tags_to_string(tags or {})}"
            self.counters[key] += value

    def record_histogram(
        self,
        name: str,
        value: float,
        tags: Dict[str, str] = None
    ):
        """Record a histogram metric (distribution of values)"""
        self.record_gauge(f"{name}.count", 1, tags)
        self.record_gauge(f"{name}.sum", value, tags)
        self.record_gauge(f"{name}.last", value, tags)

    def get_metric(
        self,
        name: str,
        since: datetime = None,
        tags: Dict[str, str] = None
    ) -> List[MetricPoint]:
        """Get metric points"""
        with self.lock:
            points = list(self.metrics[name])

            # Filter by time
            if since:
                points = [p for p in points if p.timestamp >= since]

            # Filter by tags
            if tags:
                points = [p for p in points if self._tags_match(p.tags, tags)]

            return points

    def get_counter(
        self,
        name: str,
        tags: Dict[str, str] = None
    ) -> int:
        """Get counter value"""
        with self.lock:
            key = f"{name}:{self._tags_to_string(tags or {})}"
            return self.counters.get(key, 0)

    def get_stats(
        self,
        name: str,
        since: datetime = None,
        tags: Dict[str, str] = None
    ) -> Dict[str, float]:
        """Get basic statistics for a metric"""
        points = self.get_metric(name, since, tags)

        if not points:
            return {}

        values = [p.value for p in points]

        return {
            'count': len(values),
            'min': min(values),
            'max': max(values),
            'avg': sum(values) / len(values),
            'p50': self._percentile(values, 50),
            'p95': self._percentile(values, 95),
            'p99': self._percentile(values, 99)
        }

    def _tags_to_string(self, tags: Dict[str, str]) -> str:
        """Convert tags to string for counter key"""
        return ",".join(f"{k}={v}" for k, v in sorted(tags.items()))

    def _tags_match(self, metric_tags: Dict[str, str], filter_tags: Dict[str, str]) -> bool:
        """Check if metric tags match filter tags"""
        for key, value in filter_tags.items():
            if metric_tags.get(key) != value:
                return False
        return True

    def _percentile(self, values: List[float], percentile: float) -> float:
        """Calculate percentile"""
        if not values:
            return 0

        sorted_values = sorted(values)
        index = int(len(sorted_values) * percentile / 100)
        return sorted_values[min(index, len(sorted_values) - 1)]

# Global metrics collector
metrics = MetricsCollector()

class MetricsMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive)
        start_time = time.time()

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                # Record request duration
                duration = time.time() - start_time
                status_code = message.get("status", 500)

                metrics.record_histogram(
                    "http_request_duration",
                    duration,
                    {
                        'method': request.method,
                        'status': str(status_code // 100) + 'xx',
                        'endpoint': request.url.path
                    }
                )

                # Increment request counter
                metrics.increment_counter(
                    "http_requests_total",
                    tags={
                        'method': request.method,
                        'status': str(status_code // 100) + 'xx'
                    }
                )

                # Record active requests
                metrics.increment_counter("http_requests_active", -1)

            await send(message)

        # Record active request
        metrics.increment_counter("http_requests_active")

        await self.app(scope, receive, send_wrapper)

# Performance monitoring decorator
def monitor_performance(metric_name: str, tags: Dict[str, str] = None):
    """Decorator to monitor function performance"""
    def decorator(func):
        import asyncio

        if asyncio.iscoroutinefunction(func):
            async def async_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    metrics.record_histogram(
                        f"{metric_name}.success",
                        time.time() - start_time,
                        tags
                    )
                    return result
                except Exception as e:
                    metrics.record_histogram(
                        f"{metric_name}.error",
                        time.time() - start_time,
                        {**(tags or {}), 'error': type(e).__name__}
                    )
                    raise
            return async_wrapper
        else:
            def sync_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    metrics.record_histogram(
                        f"{metric_name}.success",
                        time.time() - start_time,
                        tags
                    )
                    return result
                except Exception as e:
                    metrics.record_histogram(
                        f"{metric_name}.error",
                        time.time() - start_time,
                        {**(tags or {}), 'error': type(e).__name__}
                    )
                    raise
            return sync_wrapper
    return decorator
```

### 13.3 Health Checks

```python
# backend/app/core/health.py
from fastapi import FastAPI, Request, Response
from sqlalchemy import text
from typing import Dict, Any
import asyncio
import redis
import logging
from ..database.connection import get_db
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

class HealthChecker:
    def __init__(self):
        self.checks = {}
        self.healthy = True

    def add_check(self, name: str, check_func):
        """Add a health check function"""
        self.checks[name] = check_func

    async def run_checks(self) -> Dict[str, Any]:
        """Run all health checks"""
        results = {}
        overall_healthy = True

        for name, check_func in self.checks.items():
            try:
                result = await check_func()
                results[name] = {
                    'status': 'healthy' if result else 'unhealthy',
                    'timestamp': '2023-01-01T00:00:00Z'
                }
                if not result:
                    overall_healthy = False
            except Exception as e:
                logger.error(f"Health check {name} failed: {e}")
                results[name] = {
                    'status': 'unhealthy',
                    'error': str(e),
                    'timestamp': '2023-01-01T00:00:00Z'
                }
                overall_healthy = False

        self.healthy = overall_healthy

        return {
            'status': 'healthy' if overall_healthy else 'unhealthy',
            'checks': results,
            'timestamp': '2023-01-01T00:00:00Z'
        }

# Global health checker
health_checker = HealthChecker()

def setup_health_checks(app: FastAPI):
    """Setup health check endpoints"""

    @app.get("/health")
    async def health_check():
        """Basic health check"""
        return await health_checker.run_checks()

    @app.get("/health/ready")
    async def readiness_check():
        """Readiness check - includes dependencies"""
        return await health_checker.run_checks()

    @app.get("/health/live")
    async def liveness_check():
        """Liveness check - basic application health"""
        return {
            'status': 'healthy',
            'timestamp': '2023-01-01T00:00:00Z'
        }

# Health check functions
async def check_database():
    """Check database connectivity"""
    try:
        db = next(get_db())
        result = db.execute(text("SELECT 1"))
        return result.scalar() == 1
    except Exception:
        return False

async def check_redis():
    """Check Redis connectivity"""
    try:
        redis_client = redis.from_url(os.getenv("REDIS_URL"))
        return redis_client.ping()
    except Exception:
        return False

async def check_llm_providers():
    """Check LLM provider availability"""
    try:
        # Try to connect to at least one LLM provider
        # This is a simplified check - in production, you might want to test actual API calls
        return True
    except Exception:
        return False

async def check_disk_space():
    """Check available disk space"""
    try:
        import shutil
        total, used, free = shutil.disk_usage('/')
        # Check if free space is at least 10% of total
        return free > total * 0.1
    except Exception:
        return False

async def check_memory_usage():
    """Check memory usage"""
    try:
        import psutil
        memory = psutil.virtual_memory()
        # Check if memory usage is below 90%
        return memory.percent < 90
    except Exception:
        return True  # Fallback to healthy if we can't check

# Register health checks
health_checker.add_check("database", check_database)
health_checker.add_check("redis", check_redis)
health_checker.add_check("llm_providers", check_llm_providers)
health_checker.add_check("disk_space", check_disk_space)
health_checker.add_check("memory_usage", check_memory_usage)
```

---

## Conclusion

This comprehensive architecture document provides the technical blueprint for the VerificAI Code Quality System. The architecture is designed to be:

1. **Scalable**: Built with horizontal scaling in mind
2. **Maintainable**: Clean separation of concerns and modular design
3. **Secure**: Multiple layers of security protections
4. **Performant**: Optimized for the specific use case of code analysis
5. **Observable**: Comprehensive monitoring and logging
6. **Resilient**: Error handling, retries, and fallback mechanisms

The system leverages modern technologies and best practices while maintaining flexibility for future evolution. The monorepo structure with clear boundaries between components allows for easy migration to microservices if needed in the future.

Key architectural decisions include:
- Clean Architecture with dependency injection
- Event-driven design for async processing
- Multi-LLM integration with fallback mechanisms
- Token optimization for cost efficiency
- Comprehensive security measures
- Performance optimizations at all layers

This architecture provides a solid foundation for delivering a high-quality, AI-powered code analysis platform that meets the needs of QA teams while being prepared for future growth and feature expansion.

---

## Change Log

| Date | Version | Description | Author |
|------|--------|-----------|-------|
| 2025-09-14 | v1.0 | Initial full-stack architecture document | Claude (Architect) |