# AVALIA Supabase Integration Guide

This guide provides complete instructions for setting up and integrating Supabase with the AVALIA code analysis application.

## Overview

Supabase provides the following services for AVALIA:
- **PostgreSQL Database**: User management, analyses, prompts, and file metadata
- **Authentication**: Secure user authentication with JWT tokens
- **Storage**: File upload and management for code files and analysis reports
- **Row Level Security**: Fine-grained access control for data privacy

## Prerequisites

- Supabase CLI installed
- Node.js (for local development)
- Python 3.8+ (for backend)
- Git

### Install Supabase CLI

**macOS:**
```bash
brew install supabase/tap/supabase
```

**Windows:**
```bash
choco install supabase
```

**Linux:**
```bash
npm install -g @supabase/cli
```

## Quick Setup

### 1. Automated Setup (Recommended)

Run the automated setup script:

```bash
python supabase/scripts/setup_project.py
```

This script will:
- Create a new Supabase project
- Apply the database schema
- Set up storage buckets
- Configure authentication
- Update your environment files

### 2. Manual Setup

If you prefer manual setup, follow these steps:

#### Step 1: Create Supabase Project

1. Sign up at [supabase.com](https://supabase.com)
2. Create a new project named "avalia-code-analysis"
3. Note your project URL and API keys

#### Step 2: Initialize Local Development

```bash
cd supabase
supabase init
supabase link --project-ref YOUR_PROJECT_REF
```

#### Step 3: Apply Database Schema

```bash
# Apply the main schema
supabase db push

# Apply storage configuration
supabase db push --file storage/setup_storage.sql
```

#### Step 4: Configure Environment

Copy the template and fill in your values:

```bash
cp .env.supabase.template .env
```

Update the `.env` file with your actual Supabase credentials:
- `SUPABASE_URL`: Your project URL
- `SUPABASE_ANON_KEY`: Your anonymous key
- `SUPABASE_SERVICE_ROLE_KEY`: Your service role key
- `DATABASE_URL`: PostgreSQL connection string

## Database Schema

### Core Tables

#### profiles
User profile information extending Supabase auth.users
- id (uuid, primary key, references auth.users)
- username (text, unique)
- email (text, unique)
- role (enum: ADMIN, QA_ENGINEER, DEVELOPER, VIEWER)
- is_active (boolean)
- full_name (text)
- bio (text)
- avatar_url (text)

#### analyses
Code analysis jobs and results
- id (uuid, primary key)
- user_id (uuid, references profiles)
- prompt_id (uuid, references prompts)
- name (text)
- status (enum: pending, processing, completed, failed, cancelled)
- configuration (jsonb)
- overall_score (integer)
- security_score (integer)

#### prompts
Analysis prompts and configurations
- id (uuid, primary key)
- user_id (uuid, references profiles)
- type (enum: general, architectural, business)
- content (text)
- version (integer)
- status (enum: active, inactive, draft, archived)

#### uploaded_files
File metadata and storage information
- id (uuid, primary key)
- user_id (uuid, references profiles)
- file_id (text, unique)
- original_name (text)
- file_path (text)
- file_size (integer)
- mime_type (text)

#### general_criteria
User-defined analysis criteria
- id (uuid, primary key)
- user_id (uuid, references profiles)
- text (text)
- is_active (boolean)
- order (integer)

### Storage Buckets

#### code-files
- Purpose: Store uploaded source code files
- Access: Private, user-specific
- Size limit: 100MB per file
- Supported formats: .py, .js, .ts, .java, .cpp, .go, .rs, etc.

#### analysis-reports
- Purpose: Store generated analysis reports
- Access: Private, user-specific
- Size limit: 50MB per file
- Supported formats: PDF, JSON, CSV

#### user-avatars
- Purpose: Store user profile images
- Access: Public
- Size limit: 2MB per file
- Supported formats: JPEG, PNG, GIF, WebP

## Authentication Configuration

### Authentication Methods

1. **Email/Password**: Traditional authentication
2. **Social Login**: Google, GitHub (configurable)
3. **Magic Links**: Passwordless authentication

### User Roles

- **ADMIN**: Full system access
- **QA_ENGINEER**: Create analyses, manage prompts, view reports
- **DEVELOPER**: Create analyses, view prompts
- **VIEWER**: View analyses and reports only

### Row Level Security (RLS)

All tables have RLS policies enabled:

- Users can only access their own data
- Admins can access all data
- Public files are accessible to all users

## Integration with Backend

### FastAPI Integration

The backend includes comprehensive Supabase integration:

1. **Core Module** (`backend/app/core/supabase.py`)
   - Supabase client configuration
   - Authentication utilities
   - Storage operations
   - Database helpers

2. **Dependencies** (`backend/app/dependencies/supabase.py`)
   - FastAPI dependency injection
   - User authentication middleware
   - Permission-based access control

3. **API Routes** (`backend/app/api/v1/supabase_auth.py`)
   - Authentication endpoints
   - User profile management
   - Token verification

### Required Dependencies

Add to your `backend/requirements.txt`:

```
supabase>=1.0.0
python-dotenv>=1.0.0
```

## Integration with Frontend

### Streamlit Integration

The frontend includes a comprehensive Supabase client:

1. **Client Wrapper** (`frontend/utils/supabase_client.py`)
   - Authentication methods
   - Database operations
   - File upload/download
   - Session management

2. **Authentication Page** (`frontend/pages/auth.py`)
   - Sign up form
   - Sign in form
   - Password reset
   - User profile management

### Streamlit Secrets

Create `.streamlit/secrets.toml`:

```toml
[supabase]
url = "your-project-url.supabase.co"
anon_key = "your-anon-key"
service_role_key = "your-service-role-key"

[database]
url = "your-database-connection-string"
```

## Testing

### Run Connection Tests

```bash
python supabase/scripts/test_connection.py
```

This will test:
- Configuration validation
- Database connectivity
- Authentication services
- Storage operations
- Row level security
- Data model structure

### Test Results

All tests should pass:
- ✅ Configuration
- ✅ Connection
- ✅ Authentication
- ✅ Database Operations
- ✅ Storage Operations
- ✅ Row Level Security
- ✅ Data Models

## File Upload Process

### Backend Upload Flow

1. Client uploads file to backend API
2. Backend validates file type and size
3. Backend uploads to Supabase Storage
4. Backend creates database record with file metadata
5. Returns file information to client

### Frontend Upload Flow

1. User selects file(s) in Streamlit interface
2. File is uploaded via backend API
3. Progress tracking and error handling
4. File metadata stored in database

### Storage Path Format

```
{bucket}/{user_id}/{timestamp}_{unique_id}_{sanitized_filename}
```

Example: `code-files/12345678-1234-1234-1234-123456789012/1703123456789_abc123_main.py`

## Security Features

### Authentication Security

- JWT-based authentication
- Secure password hashing (handled by Supabase)
- Session management
- Token expiration handling

### Data Security

- Row Level Security (RLS) on all tables
- User-specific data isolation
- Admin override capabilities
- Encrypted data transmission

### File Security

- Private storage buckets
- User-specific file paths
- File type validation
- Size restrictions
- Malware scanning (can be added)

## Monitoring and Analytics

### Database Monitoring

Monitor through Supabase Dashboard:
- Query performance
- Connection usage
- Storage utilization
- User activity

### Application Monitoring

Add to your backend application:
- Request logging
- Error tracking
- Performance metrics
- User analytics

## Deployment Considerations

### Production Setup

1. **Environment Variables**: Secure management of secrets
2. **Backup Strategy**: Regular database backups
3. **Scaling**: Connection pooling and read replicas
4. **Security**: Network restrictions, audit logs

### Migration Strategy

1. Test migrations in staging
2. Backup before migration
3. Plan for rollback
4. Monitor post-migration performance

## Troubleshooting

### Common Issues

#### Connection Failures
- Verify environment variables
- Check network connectivity
- Validate API keys
- Ensure correct project reference

#### Authentication Issues
- Check JWT token format
- Verify user registration
- Confirm email verification status
- Check RLS policies

#### Storage Issues
- Verify bucket permissions
- Check file size limits
- Validate file formats
- Confirm user access rights

### Debug Mode

Enable debug logging by setting:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Support Resources

- [Supabase Documentation](https://supabase.com/docs)
- [AVALIA Project Issues](https://github.com/your-avalia-repo/issues)
- [Supabase Community](https://github.com/supabase/supabase/discussions)

## Performance Optimization

### Database Optimization

- Add appropriate indexes
- Use connection pooling
- Optimize queries
- Implement caching

### Storage Optimization

- Implement file compression
- Use CDN for public assets
- Implement file cleanup
- Monitor storage usage

### Application Optimization

- Implement request caching
- Use async operations
- Optimize batch operations
- Monitor response times

## Next Steps

After completing the Supabase setup:

1. **Test Integration**: Run all test scripts
2. **Deploy Backend**: Update backend configuration
3. **Update Frontend**: Configure Streamlit secrets
4. **User Testing**: Test authentication and file upload
5. **Performance Testing**: Load test with multiple users
6. **Security Audit**: Review access controls and policies

## Contributing

When contributing to the Supabase integration:

1. Test all database migrations
2. Verify RLS policies
3. Update documentation
4. Add tests for new features
5. Follow security best practices

## License

This Supabase integration follows the same license as the AVALIA project.