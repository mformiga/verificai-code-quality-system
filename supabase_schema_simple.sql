-- AVALIA Code Analysis - Supabase Database Schema (Simplified)
-- Execute this in your Supabase SQL Editor

-- Create profiles table
CREATE TABLE IF NOT EXISTS public.profiles (
    id uuid REFERENCES auth.users(id) PRIMARY KEY,
    username text,
    full_name text,
    role text DEFAULT 'user',
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now()
);

-- Create analyses table
CREATE TABLE IF NOT EXISTS public.analyses (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id uuid REFERENCES public.profiles(id) ON DELETE CASCADE,
    file_path text NOT NULL,
    analysis_type text DEFAULT 'local',
    criteria_count integer DEFAULT 0,
    violation_count integer DEFAULT 0,
    analysis_data jsonb,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now()
);

-- Create analysis results table
CREATE TABLE IF NOT EXISTS public.analysis_results (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    analysis_id uuid REFERENCES public.analyses(id) ON DELETE CASCADE,
    criterion_id text NOT NULL,
    analysis_text text,
    violations text[],
    violation_count integer DEFAULT 0,
    created_at timestamptz DEFAULT now()
);

-- Create uploaded files table
CREATE TABLE IF NOT EXISTS public.uploaded_files (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id uuid REFERENCES public.profiles(id) ON DELETE CASCADE,
    file_name text NOT NULL,
    file_path text NOT NULL,
    bucket text DEFAULT 'code-files',
    file_size integer,
    mime_type text,
    created_at timestamptz DEFAULT now()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_analyses_user_id ON public.analyses(user_id);
CREATE INDEX IF NOT EXISTS idx_analyses_created_at ON public.analyses(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_analysis_results_analysis_id ON public.analysis_results(analysis_id);
CREATE INDEX IF NOT EXISTS idx_uploaded_files_user_id ON public.uploaded_files(user_id);

-- Enable Row Level Security
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.analysis_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.uploaded_files ENABLE ROW LEVEL SECURITY;

-- RLS Policies for profiles
CREATE POLICY "Users can view own profile" ON public.profiles
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can insert own profile" ON public.profiles
    FOR INSERT WITH CHECK (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON public.profiles
    FOR UPDATE USING (auth.uid() = id);

-- RLS Policies for analyses
CREATE POLICY "Users can view own analyses" ON public.analyses
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own analyses" ON public.analyses
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own analyses" ON public.analyses
    FOR UPDATE USING (auth.uid() = user_id);

-- RLS Policies for analysis results
CREATE POLICY "Users can view own analysis results" ON public.analysis_results
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.analyses
            WHERE id = public.analysis_results.analysis_id
            AND public.analyses.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert own analysis results" ON public.analysis_results
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.analyses
            WHERE id = public.analysis_results.analysis_id
            AND public.analyses.user_id = auth.uid()
        )
    );

-- RLS Policies for uploaded files
CREATE POLICY "Users can view own files" ON public.uploaded_files
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own files" ON public.uploaded_files
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Function to handle new user registration
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, username)
    VALUES (new.id, new.raw_user_meta_data->>'username')
    ON CONFLICT (id) DO UPDATE SET updated_at = now();
    RETURN new;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to create profile on user signup
CREATE OR REPLACE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Test connection table
CREATE TABLE IF NOT EXISTS public.test_connection (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    message text DEFAULT 'AVALIA connected successfully!',
    created_at timestamptz DEFAULT now()
);

-- Enable RLS for test table
ALTER TABLE public.test_connection ENABLE ROW LEVEL SECURITY;

-- RLS policy for test table
CREATE POLICY "Anyone can view test table" ON public.test_connection
    FOR SELECT USING (true);

CREATE POLICY "Anyone can insert test table" ON public.test_connection
    FOR INSERT WITH CHECK (true);

-- Insert test record
INSERT INTO public.test_connection (message)
VALUES ('AVALIA application database setup complete!');

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'AVALIA database schema created successfully!';
END $$;