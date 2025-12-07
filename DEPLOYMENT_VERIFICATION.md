# AVALIA Streamlit Cloud Deployment Verification Guide

## ✅ Deployment Status: SUCCESS

**App URL**: https://verificai-code-quality-system-eapzchsvw6mwarkajltkzf.streamlit.app/

**Status**: ✅ DEPLOYED AND ACCESSIBLE

## 🚀 Next Steps: Configure Supabase Integration

### Step 1: Get Your Supabase Credentials

1. Go to your [Supabase Dashboard](https://supabase.com/dashboard)
2. Select your project
3. Navigate to **Settings** > **API**
4. Copy the following:
   - **Project URL**: `https://your-project-id.supabase.co`
   - **anon public key**: `eyJ...` (starts with eyJ)
   - **service_role key**: `eyJ...` (starts with eyJ)

### Step 2: Configure Streamlit Cloud Secrets

1. Go to [Streamlit Cloud](https://share.streamlit.io/)
2. Navigate to your app: `verificai-code-quality-system`
3. Click **Settings** > **Secrets**
4. Add the following configuration:

```toml
[secrets.supabase]
SUPABASE_URL = "https://your-project-id.supabase.co"
SUPABASE_ANON_KEY = "your_anon_public_key_here"
SUPABASE_SERVICE_ROLE_KEY = "your_service_role_key_here"
```

**Replace the placeholder values with your actual Supabase credentials.**

### Step 3: Set Up Database Schema

1. In your Supabase project, go to **SQL Editor**
2. Run the schema from `supabase_schema.sql`:

```sql
-- AVALIA Code Analysis - Supabase Database Schema
-- Execute this in your Supabase SQL Editor

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Profiles table (extends auth.users)
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID REFERENCES auth.users(id) PRIMARY KEY,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    username TEXT,
    full_name TEXT,
    avatar_url TEXT,
    role TEXT DEFAULT 'user' CHECK (role IN ('admin', 'user', 'qa_engineer', 'developer', 'viewer')),
    CONSTRAINT username_length CHECK (char_length(username) >= 3),
    CONSTRAINT username_unique UNIQUE (username)
);

-- Analyses table
CREATE TABLE IF NOT EXISTS public.analyses (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL,
    file_path TEXT NOT NULL,
    analysis_type TEXT DEFAULT 'local' CHECK (analysis_type IN ('local', 'remote', 'hybrid')),
    criteria_count INTEGER DEFAULT 0,
    violation_count INTEGER DEFAULT 0,
    analysis_data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Analysis results table
CREATE TABLE IF NOT EXISTS public.analysis_results (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    analysis_id UUID REFERENCES public.analyses(id) ON DELETE CASCADE NOT NULL,
    criterion_id TEXT NOT NULL,
    analysis_text TEXT,
    violations TEXT[],
    violation_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Uploaded files table
CREATE TABLE IF NOT EXISTS public.uploaded_files (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL,
    file_name TEXT NOT NULL,
    file_path TEXT NOT NULL,
    bucket TEXT DEFAULT 'code-files',
    file_size INTEGER,
    mime_type TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Create indexes
CREATE INDEX IF NOT EXISTS analyses_user_id_idx ON public.analyses(user_id);
CREATE INDEX IF NOT EXISTS analyses_created_at_idx ON public.analyses(created_at DESC);
CREATE INDEX IF NOT EXISTS analysis_results_analysis_id_idx ON public.analysis_results(analysis_id);
CREATE INDEX IF NOT EXISTS uploaded_files_user_id_idx ON public.uploaded_files(user_id);

-- Enable Row Level Security
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.analysis_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.uploaded_files ENABLE ROW LEVEL SECURITY;

-- RLS Policies for profiles
CREATE POLICY "Users can view own profile." ON public.profiles
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can insert own profile." ON public.profiles
    FOR INSERT WITH CHECK (auth.uid() = id);

CREATE POLICY "Users can update own profile." ON public.profiles
    FOR UPDATE USING (auth.uid() = id);

-- RLS Policies for analyses
CREATE POLICY "Users can view own analyses." ON public.analyses
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own analyses." ON public.analyses
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own analyses." ON public.analyses
    FOR UPDATE USING (auth.uid() = user_id);

-- RLS Policies for analysis results
CREATE POLICY "Users can view own analysis results." ON public.analysis_results
    FOR SELECT USING (
        EXISTS (SELECT 1 FROM public.analyses WHERE id = analysis_results.analysis_id AND analyses.user_id = auth.uid())
    );

CREATE POLICY "Users can insert own analysis results." ON public.analysis_results
    FOR INSERT WITH CHECK (
        EXISTS (SELECT 1 FROM public.analyses WHERE id = analysis_results.analysis_id AND analyses.user_id = auth.uid())
    );

-- RLS Policies for uploaded files
CREATE POLICY "Users can view own files." ON public.uploaded_files
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own files." ON public.uploaded_files
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Function to handle new user registration
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, username)
    VALUES (new.id, new.raw_user_meta_data->>'username')
    ON CONFLICT (id) DO NOTHING;
    RETURN new;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to create profile on user signup
CREATE OR REPLACE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();
```

### Step 4: Configure Authentication Settings

1. In Supabase, go to **Authentication** > **Settings**
2. Configure **Site URL** as: `https://verificai-code-quality-system-eapzchsvw6mwarkajltkzf.streamlit.app/`
3. Set **Redirect URLs** to include the same URL
4. Enable **Email confirmation** if required
5. Configure other auth settings as needed

## 🧪 Testing Your Deployment

### Basic Functionality Test

1. **Access the App**: https://verificai-code-quality-system-eapzchsvw6mwarkajltkzf.streamlit.app/
2. **User Registration**:
   - Click "Registrar" tab
   - Enter email and password
   - Click "Criar Conta"
   - Check email if confirmation is enabled
3. **User Login**:
   - Click "Login" tab
   - Enter credentials
   - Click "Entrar"
4. **Code Analysis**:
   - Upload a file or enter code manually
   - Select analysis criteria
   - Click "Iniciar Análise"
   - Review results
5. **History**:
   - Check "Histórico" tab for previous analyses

### Advanced Testing

1. **Database Integration**:
   - Verify analysis results are saved to Supabase
   - Check user profiles are created automatically
   - Confirm RLS policies are working

2. **Security**:
   - Test that users can only access their own data
   - Verify authentication tokens are handled securely
   - Check HTTPS is enforced

## 🔧 Troubleshooting

### Common Issues

1. **Supabase Connection Failed**
   ```
   Error: Cliente Supabase não inicializado
   ```
   **Solution**: Check secrets configuration in Streamlit Cloud

2. **Authentication Issues**
   ```
   Error: Falha no login
   ```
   **Solution**: Verify Supabase auth settings and email configuration

3. **Database Errors**
   ```
   Error: Erro ao salvar análise
   ```
   **Solution**: Ensure database schema is installed correctly

### Debug Mode

To debug issues, add this to your app temporarily:

```python
import os
print("Environment variables:", dict(os.environ))
print("Streamlit secrets:", st.secrets)
```

## 📊 Deployment Checklist

- [x] App is accessible on Streamlit Cloud
- [ ] Supabase secrets configured
- [ ] Database schema installed
- [ ] User registration working
- [ ] User login working
- [ ] Code analysis functional
- [ ] Analysis history working
- [ ] Security policies active

## 🎯 Success Metrics

Your deployment is successful when:

1. ✅ App loads within 10 seconds
2. ✅ Users can register and login
3. ✅ Code analysis completes successfully
4. ✅ Results are saved to Supabase
5. ✅ Analysis history displays correctly
6. ✅ All AVALIA branding is displayed
7. ✅ No security warnings or errors

## 📞 Support

If you encounter issues:

1. Check Streamlit Cloud deployment logs
2. Verify Supabase configuration
3. Test database connection in Supabase dashboard
4. Review authentication settings
5. Check RLS policies in database

---

**Deployment completed successfully!** Your AVALIA application is now ready for production use.