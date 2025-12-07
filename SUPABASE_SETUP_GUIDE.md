# AVALIA Supabase Setup Guide

## Step 3: Database Schema Setup

### 3.1 Run the Initial Schema Migration

In your Supabase Dashboard:
1. Go to **SQL Editor**
2. Create a new query
3. Copy and paste the contents of `supabase/migrations/001_initial_schema.sql`
4. **Execute** the query

This will create:
- `profiles` table (user profiles extending auth.users)
- `prompts` table (analysis prompts)
- `general_criteria` table (user-defined analysis criteria)
- `analyses` table (code analysis jobs)
- `analysis_results` table (detailed analysis results)
- `general_analysis_results` table (general analysis format)
- `uploaded_files` table (file upload tracking)
- All necessary indexes and RLS policies

### 3.2 Set Up Storage Buckets

1. Go to **Storage** in the Supabase Dashboard
2. Create a new bucket named `code-files`
3. Set file size limit to 100MB
4. Run the storage setup SQL from `supabase/storage/setup_storage.sql`

## Step 4: Authentication Configuration

### 4.1 Email/Password Authentication

In **Authentication → Settings**:
1. Enable **Email auth**
2. Set **Site URL** to `http://localhost:3000` (for development)
3. Add **Redirect URLs**:
   - `http://localhost:3000`
   - `http://localhost:5173` (Vite default)
   - Your production domain when deployed

### 4.2 OAuth Providers (Optional but Recommended)

Enable these providers if desired:
- **GitHub** (for developers)
- **Google** (for general users)

### 4.3 Email Templates

Customize email templates:
1. Go to **Authentication → Email Templates**
2. Customize **Confirm signup**, **Magic Link**, and **Reset Password** templates
3. Include AVALIA branding

## Step 5: Row Level Security (RLS) Configuration

The schema migration already enables RLS on all tables and creates appropriate policies. Verify:
- All tables have RLS enabled
- Users can only access their own data
- Admins have appropriate access

## Step 6: Environment Configuration

Create `.env.supabase` file with:

```bash
# AVALIA Supabase Configuration
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here
SUPABASE_PROJECT_REF=your-project-ref

# Database Configuration
DATABASE_URL=postgresql://postgres.iamuser:[YOUR-PASSWORD]@aws-0-us-west-1.pooler.supabase.com:5432/postgres

# Authentication
JWT_SECRET=your-jwt-secret-from-supabase
SUPABASE_JWT_SECRET=your-jwt-secret-from-supabase

# Storage Configuration
STORAGE_URL=https://your-project-ref.supabase.co/storage/v1
STORAGE_REGION=us-west-1
```

## Step 7: Test Connection

Run the test script to verify everything works:

```bash
python supabase/scripts/test_connection.py
```

## Step 8: Verify Setup

1. **Authentication Test**: Try signing up a new user
2. **Database Test**: Create a test analysis
3. **Storage Test**: Upload a sample file
4. **RLS Test**: Verify users can only see their own data

## Troubleshooting

### Common Issues:

1. **CORS Errors**: Ensure your frontend URL is in the allowed redirect URLs
2. **Authentication Failures**: Check JWT secrets match
3. **Storage Access**: Verify RLS policies for storage buckets
4. **Database Connection**: Ensure database URL is correct and password is valid

### Helpful Queries:

```sql
-- Check RLS is enabled
SELECT schemaname, tablename, rowsecurity
FROM pg_tables
WHERE schemaname = 'public';

-- Check user profiles
SELECT * FROM public.profiles;

-- Check recent analyses
SELECT * FROM public.analyses ORDER BY created_at DESC LIMIT 5;
```

## Production Considerations

1. **Enable SSL**: Ensure all connections use HTTPS
2. **Restrict API Keys**: Use service role key only in backend
3. **Monitor Usage**: Set up alerts for database and storage usage
4. **Backups**: Enable automated backups
5. **Rate Limiting**: Configure API rate limits
6. **Audit Logs**: Enable audit logging for compliance