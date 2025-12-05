# AVALIA Streamlit Cloud Deployment Guide

## Prerequisites
1. Supabase project set up with the schema from `supabase_schema.sql`
2. Streamlit Cloud account
3. GitHub repository with the code

## Step 1: Configure Supabase

1. Go to your Supabase project dashboard
2. Navigate to Settings > API
3. Copy the following values:
   - Project URL
   - anon public key
   - service_role key (keep this secret!)

## Step 2: Set up Streamlit Cloud Secrets

In your Streamlit Cloud dashboard:

1. Go to your app settings
2. Click on "Secrets"
3. Add the following configuration:

```toml
[secrets.supabase]
SUPABASE_URL = "https://your-project-id.supabase.co"
SUPABASE_ANON_KEY = "your_anon_public_key_here"
SUPABASE_SERVICE_ROLE_KEY = "your_service_role_key_here"
```

## Step 3: Deploy to Streamlit Cloud

1. Connect your GitHub repository to Streamlit Cloud
2. Select the repository containing the AVALIA code
3. Configure the deployment:
   - Main file path: `app.py`
   - Python version: 3.11 (recommended)
   - Hardware: Standard (free tier should work for testing)

## Step 4: Verify Deployment

After deployment, your app should be available at:
https://verificai-code-quality-system-eapzchsvw6mwarkajltkzf.streamlit.app/

## Testing Checklist

### 1. Authentication Test
- [ ] User registration works
- [ ] User login works
- [ ] Session persistence
- [ ] Logout functionality

### 2. Database Connection Test
- [ ] Connection to Supabase established
- [ ] User profiles created automatically
- [ ] Analysis results saved
- [ ] Analysis history loaded

### 3. Core Functionality Test
- [ ] Code analysis works
- [ ] Criteria selection functional
- [ ] Results display correctly
- [ ] File upload works

### 4. Security Test
- [ ] Row Level Security (RLS) policies active
- [ ] Users can only access their own data
- [ ] Proper error handling

## Troubleshooting

### Common Issues:

1. **Supabase Connection Failed**
   - Check secrets configuration
   - Verify URL and keys are correct
   - Ensure Supabase project is active

2. **Authentication Issues**
   - Verify email confirmation is enabled in Supabase
   - Check RLS policies
   - Ensure auth schema is properly set up

3. **Database Issues**
   - Run the schema setup in Supabase SQL Editor
   - Check table permissions
   - Verify triggers are created

4. **Deployment Failures**
   - Check requirements.txt has correct dependencies
   - Ensure app.py is in root directory
   - Verify Python version compatibility

## Required Environment Variables

For local development, create a `.env.supabase` file:

```
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your_anon_public_key_here
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here
```

## Next Steps After Deployment

1. Configure custom domain (if needed)
2. Set up monitoring and logging
3. Configure backup for Supabase
4. Set up user management workflow
5. Add rate limiting if needed

## Support

For issues:
- Streamlit Cloud documentation
- Supabase documentation
- Application logs in Streamlit Cloud dashboard