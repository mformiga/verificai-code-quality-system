# Streamlit + Supabase Integration Guide

## Overview
This guide shows how to configure your AVALIA Streamlit application to work with Supabase for authentication, database, and file storage.

## Step 1: Create Supabase Project

1. Go to [https://app.supabase.com](https://app.supabase.com)
2. Click **"New Project"**
3. Choose **Organization** or create one
4. Project Name: `AVALIA Code Analysis`
5. Database Password: Create a strong password (save it!)
6. Region: Choose the nearest region to you
7. Click **"Create new project"**
8. Wait 2-3 minutes for project creation

## Step 2: Get Supabase Credentials

1. In your Supabase project dashboard, go to **Project Settings**
2. Click on **API** in the sidebar
3. You'll see these credentials:
   - **Project URL**: `https://your-project-ref.supabase.co`
   - **anon public key**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
   - **service_role key**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

## Step 3: Configure Database Schema

1. In Supabase dashboard, go to **SQL Editor**
2. Click **"New query"**
3. Copy the contents of `supabase_schema.sql`
4. Click **"Run"** to execute

This will create:
- `profiles` table (user profiles)
- `analyses` table (code analysis results)
- `analysis_results` table (detailed results)
- `uploaded_files` table (file metadata)
- Row Level Security policies
- Triggers for user registration

## Step 4: Configure Storage Buckets

1. Go to **Storage** in the Supabase dashboard
2. Click **"New bucket"**
3. Create these buckets:

### Bucket 1: code-files
- Name: `code-files`
- Public bucket: **No**
- File size limit: `100MB`
- Allowed file types: `.py, .js, .ts, .java, .cpp, .c, .php, .rb, .go`

### Bucket 2: analysis-reports
- Name: `analysis-reports`
- Public bucket: **No**
- File size limit: `50MB`

## Step 5: Update Environment Configuration

### Local Development

Edit your `.env.supabase` file:

```bash
# Replace these with your actual Supabase credentials
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.your-actual-anon-key
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.your-actual-service-key
SUPABASE_PROJECT_REF=your-project-ref
ENVIRONMENT=development
```

### Streamlit Cloud Deployment

1. Go to your Streamlit Cloud workspace
2. Click on your app
3. Go to **Settings** → **Secrets**
4. Add these secrets:

```toml
SUPABASE_URL = "https://your-project-ref.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.your-actual-anon-key"
SUPABASE_SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.your-actual-service-key"
SUPABASE_PROJECT_REF = "your-project-ref"
```

## Step 6: Test Your Application

### Local Testing

```bash
streamlit run app.py --server.port 3011
```

The application should now:

1. ✅ Show login/register screens
2. ✅ Connect to Supabase database
3. ✅ Allow user registration
4. ✅ Save analysis results to database
5. ✅ Load analysis history
6. ✅ Store uploaded files

### Expected Behavior

- **New Users**: Register with email and password
- **Existing Users**: Login with email and password
- **Analyses**: Automatically saved to Supabase
- **History**: View all your previous analyses
- **Files**: Stored securely in Supabase Storage

## Troubleshooting

### Common Issues

1. **"Cliente Supabase não inicializado"**
   - Check your .env.supabase file
   - Verify SUPABASE_URL and SUPABASE_ANON_KEY are correct

2. **"Erro no login"**
   - Make sure email format is valid
   - Check password strength (min 6 characters)
   - Verify user exists in auth.users table

3. **Database connection issues**
   - Run the schema SQL in Supabase SQL Editor
   - Check Row Level Security policies

4. **File upload errors**
   - Verify storage buckets exist
   - Check bucket permissions
   - Ensure file size is within limits

### Debug Mode

Add this to your app.py for debugging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Security Features Implemented

- ✅ **JWT Authentication** via Supabase Auth
- ✅ **Row Level Security (RLS)** on all tables
- ✅ **User data isolation** (users only see their own data)
- ✅ **Secure file storage** with per-user access
- ✅ **Password requirements** (min 6 characters)
- ✅ **Email validation** for registration
- ✅ **Session management** with token refresh

## Production Checklist

Before deploying to production:

- [ ] Supabase project created
- [ ] Database schema applied
- [ ] Storage buckets configured
- [ ] Environment variables set
- [ ] Local testing completed
- [ ] Streamlit Cloud secrets configured
- [ ] Production testing completed

## Next Steps

Once your Supabase integration is working:

1. **Deploy to Streamlit Cloud** with secrets configured
2. **Monitor your Supabase usage** in the dashboard
3. **Set up database backups** (Supabase does this automatically)
4. **Consider Supabase Pro Plan** for higher limits if needed

Your AVALIA application now has a complete backend with PostgreSQL database, authentication, and file storage powered by Supabase!