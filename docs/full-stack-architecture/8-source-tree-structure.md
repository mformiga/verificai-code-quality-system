# 8. Source Tree Structure

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
