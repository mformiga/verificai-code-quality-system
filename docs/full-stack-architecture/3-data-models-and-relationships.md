# 3. Data Models and Relationships

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
