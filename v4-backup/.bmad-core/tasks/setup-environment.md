# Setup Environment for VerificAI Code Quality System

## Overview
This task automates the setup of the development environment for the VerificAI Code Quality System, ensuring consistent configuration across all development sessions.

## Prerequisites
- Node.js >= 18.0.0
- Python >= 3.8
- npm >= 8.0.0

## Environment Configuration

### Current Working Setup (as of 2025-09-16)

#### Backend Configuration
- **Framework**: FastAPI with Python
- **Database**: SQLite (backend/verificai.db)
- **Port**: 8000
- **Start Command**: `cd backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`

#### Frontend Configuration
- **Framework**: React with Vite
- **Port**: Dynamic (starts at 3011, finds first available)
- **Start Command**: `cd frontend && npm run dev`

#### Key Fixes Applied
1. **FileUpload Component**: Simplified to remove external dependencies
2. **useFileUpload Hook**: Created standalone version without complex service dependencies
3. **Import Issues**: Resolved by defining types inline in FileUpload component

## Automatic Setup Commands

### Quick Start (All Services)
```bash
# Install all dependencies
npm run install:all

# Start both frontend and backend
npm run dev
```

### Individual Service Start
```bash
# Start backend only
npm run dev:backend

# Start frontend only
npm run dev:frontend
```

## Environment Variables

### Backend (.env)
```
DATABASE_URL=sqlite:///./verificai.db
SECRET_KEY=your-secret-key-here-change-in-production
JWT_SECRET_KEY=your-jwt-secret-key-here
DEBUG=true
```

### Frontend (.env)
```
VITE_API_BASE_URL=/api
VITE_APP_VERSION=1.0.0
VITE_ENVIRONMENT=development
```

## Database Setup
- Uses SQLite automatically created at `backend/verificai.db`
- Tables are created automatically on backend startup
- No manual migration required for development

## API Endpoints
- **Backend API**: http://localhost:8000/api/v1/
- **Backend Docs**: http://localhost:8000/api/v1/docs
- **Frontend**: Dynamic port (check console output)

## Common Issues and Solutions

### Port Conflicts
- Frontend automatically finds available port starting from 3011
- Backend uses fixed port 8000
- If port 8000 is in use, change in backend/app/core/config.py

### Import Errors
- FileUpload component is now self-contained
- All types are defined inline to avoid import issues
- No external hook dependencies for upload functionality

### Database Issues
- SQLite database is created automatically
- If corrupted, delete `backend/verificai.db` and restart backend

## Development Workflow
1. Make code changes
2. Backend auto-reloads with uvicorn
3. Frontend hot-reloads with Vite
4. Both services watch for file changes

## Testing
```bash
# Run all tests
npm test

# Run linting
npm run lint

# Run type checking
npm run typecheck
```