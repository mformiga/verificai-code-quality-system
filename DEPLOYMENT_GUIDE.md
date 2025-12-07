# verificAI - Deployment Guide

## Overview
This application is ready for deployment with support for both local PostgreSQL and remote Supabase databases. The system automatically detects the environment and uses the appropriate database.

## Environment Detection
- **Local Development**: Uses PostgreSQL local database
- **Production (Streamlit Cloud)**: Uses Supabase remote database

## Prerequisites

### Local Development
- PostgreSQL installed and running
- Database `verificai` created with user `verificai`
- Python 3.11+ with requirements.txt dependencies

### Production Deployment
- Supabase account and project
- Streamlit Cloud account
- All source codes in git repository

## Setup Instructions

### 1. Local Development Setup

1. **Install Dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set up Local PostgreSQL:**
```sql
CREATE DATABASE verificai;
CREATE USER verificai WITH PASSWORD 'verificai123';
GRANT ALL PRIVILEGES ON DATABASE verificai TO verificai;
```

3. **Run Local Application:**
```bash
streamlit run app.py --server.port 8506
```

### 2. Production Setup (Supabase + Streamlit Cloud)

#### Step 1: Configure Supabase

1. **Create Supabase Project:**
   - Go to [supabase.com](https://supabase.com)
   - Sign up and create a new project
   - Note your Project URL and API Key

2. **Run Setup Script:**
```bash
python setup_supabase.py
```

3. **Manual Setup (if script fails):**
   - Go to Supabase Dashboard > SQL Editor
   - Run the SQL from `setup_supabase.py` output

#### Step 2: Configure Secrets

**For Local Testing (.streamlit/secrets.toml):**
```toml
SUPABASE_URL = "https://your-project-ref.supabase.co"
SUPABASE_KEY = "your-supabase-anon-key"
ENVIRONMENT = "production"
```

**For Streamlit Cloud:**
1. Deploy your app to Streamlit Cloud
2. Go to App Settings > Secrets
3. Add these secrets:
   - `SUPABASE_URL`: Your Supabase project URL
   - `SUPABASE_KEY`: Your Supabase anon key
   - `ENVIRONMENT`: `production`

#### Step 3: Deploy to Streamlit Cloud

1. **Connect Repository:**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub repository
   - Select the correct branch

2. **Configure Settings:**
   - Python version: 3.11
   - Requirements file: `requirements.txt`
   - Main script: `app.py`

3. **Add Secrets:**
   - Add the Supabase secrets as shown above

4. **Deploy:**
   - Click "Deploy" and wait for completion

## Features Available

### ✅ Core Functionality
- **Code Upload**: Text field for source code content (1GB limit)
- **Multi-language Support**: 25+ programming languages detected
- **Local Storage**: PostgreSQL for development
- **Remote Storage**: Supabase for production
- **Soft Delete**: Codes are marked as deleted, not permanently removed
- **Real-time Statistics**: Line count, character count, file size

### ✅ User Interface
- **Upload Form**: Title, description, language selection
- **Code Display**: Syntax-highlighted code viewer
- **Management**: View, save, and delete operations
- **Responsive Design**: Works on desktop and mobile

### ✅ Database Integration
- **Automatic Environment Detection**: Local vs Production
- **Dual Database Support**: PostgreSQL + Supabase
- **Data Synchronization**: Seamless switching between environments
- **Row Level Security**: RLS policies for secure data access

## File Structure

```
verificAI-code/
├── app.py                    # Main Streamlit application
├── requirements.txt          # Python dependencies
├── setup_supabase.py        # Supabase setup script
├── .streamlit/
│   └── secrets.toml         # Local secrets configuration
├── backend/                 # FastAPI backend (not used in current version)
└── frontend/               # React frontend (not used in current version)
```

## Troubleshooting

### Common Issues

1. **"No database available" Error:**
   - Local: Check PostgreSQL connection
   - Production: Verify Supabase secrets

2. **"Supabase not configured" Error:**
   - Check secrets configuration
   - Verify SUPABASE_URL and SUPABASE_KEY

3. **Unicode Encoding Issues:**
   - Application handles encoding automatically
   - All Unicode characters removed for Windows compatibility

4. **Code Not Saving:**
   - Check database connection
   - Verify table exists in database
   - Check application logs

### Debug Mode

Add debug information by checking console output when running locally.

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SUPABASE_URL` | Supabase project URL | - |
| `SUPABASE_KEY` | Supabase anon key | - |
| `ENVIRONMENT` | Environment type | `development` |
| `POSTGRES_HOST` | PostgreSQL host | `localhost` |
| `POSTGRES_PORT` | PostgreSQL port | `5432` |
| `POSTGRES_DB` | PostgreSQL database | `verificai` |
| `POSTGRES_USER` | PostgreSQL user | `verificai` |
| `POSTGRES_PASSWORD` | PostgreSQL password | `verificai123` |

## Support

For issues or questions:
1. Check this deployment guide
2. Review application logs
3. Verify database connections
4. Check secrets configuration