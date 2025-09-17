# 4. Component Design

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
