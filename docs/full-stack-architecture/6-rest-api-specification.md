# 6. REST API Specification

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
