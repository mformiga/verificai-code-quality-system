-- AVALIA Code Analysis - Supabase Database Schema (Fixed)
-- Execute this in your Supabase SQL Editor

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Profiles table (extends auth.users)
CREATE TABLE IF NOT EXISTS public.profiles (
    id uuid REFERENCES auth.users(id) PRIMARY KEY,
    updated_at timestamptz DEFAULT timezone('utc'::text, now()) NOT NULL,
    username text,
    full_name text,
    avatar_url text,
    role text DEFAULT 'user' CHECK (role IN ('admin', 'user', 'qa_engineer', 'developer', 'viewer')),

    CONSTRAINT username_length CHECK (char_length(username) >= 3),
    CONSTRAINT username_unique UNIQUE (username)
);

-- Analyses table
CREATE TABLE IF NOT EXISTS public.analyses (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id uuid REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL,
    file_path text NOT NULL,
    analysis_type text DEFAULT 'local' CHECK (analysis_type IN ('local', 'remote', 'hybrid')),
    criteria_count integer DEFAULT 0,
    violation_count integer DEFAULT 0,
    analysis_data jsonb NOT NULL,
    created_at timestamptz DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at timestamptz DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Analysis results table
CREATE TABLE IF NOT EXISTS public.analysis_results (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    analysis_id uuid REFERENCES public.analyses(id) ON DELETE CASCADE NOT NULL,
    criterion_id text NOT NULL,
    analysis_text text,
    violations text[],
    violation_count integer DEFAULT 0,
    created_at timestamptz DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Uploaded files table
CREATE TABLE IF NOT EXISTS public.uploaded_files (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id uuid REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL,
    file_name text NOT NULL,
    file_path text NOT NULL,
    bucket text DEFAULT 'code-files',
    file_size integer,
    mime_type text,
    created_at timestamptz DEFAULT timezone('utc'::text, now()) NOT NULL
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
    FOR SELECT USING (auth.uid()::text = id::text);

CREATE POLICY "Users can insert own profile." ON public.profiles
    FOR INSERT WITH CHECK (auth.uid()::text = id::text);

CREATE POLICY "Users can update own profile." ON public.profiles
    FOR UPDATE USING (auth.uid()::text = id::text);

-- RLS Policies for analyses
CREATE POLICY "Users can view own analyses." ON public.analyses
    FOR SELECT USING (auth.uid()::text = user_id::text);

CREATE POLICY "Users can insert own analyses." ON public.analyses
    FOR INSERT WITH CHECK (auth.uid()::text = user_id::text);

CREATE POLICY "Users can update own analyses." ON public.analyses
    FOR UPDATE USING (auth.uid()::text = user_id::text);

-- RLS Policies for analysis results
CREATE POLICY "Users can view own analysis results." ON public.analysis_results
    FOR SELECT USING (
        EXISTS (SELECT 1 FROM public.analyses WHERE id = analysis_results.analysis_id AND analyses.user_id::text = auth.uid()::text)
    );

CREATE POLICY "Users can insert own analysis results." ON public.analysis_results
    FOR INSERT WITH CHECK (
        EXISTS (SELECT 1 FROM public.analyses WHERE id = analysis_results.analysis_id AND analyses.user_id::text = auth.uid()::text)
    );

-- RLS Policies for uploaded files
CREATE POLICY "Users can view own files." ON public.uploaded_files
    FOR SELECT USING (auth.uid()::text = user_id::text);

CREATE POLICY "Users can insert own files." ON public.uploaded_files
    FOR INSERT WITH CHECK (auth.uid()::text = user_id::text);

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

-- Create a simple test table to verify connection
CREATE TABLE IF NOT EXISTS public.test_connection (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    message text DEFAULT 'Connection successful',
    created_at timestamptz DEFAULT timezone('utc'::text, now())
);

-- Enable RLS for test table
ALTER TABLE public.test_connection ENABLE ROW LEVEL SECURITY;

-- Simple RLS policy for test table
CREATE POLICY "Everyone can view test connection" ON public.test_connection
    FOR SELECT USING (true);

CREATE POLICY "Everyone can insert test connection" ON public.test_connection
    FOR INSERT WITH CHECK (true);

-- Insert a test record
INSERT INTO public.test_connection (message) VALUES ('AVALIA application connected successfully!');

-- Grant necessary permissions
GRANT ALL ON public.profiles TO authenticated;
GRANT ALL ON public.analyses TO authenticated;
GRANT ALL ON public.analysis_results TO authenticated;
GRANT ALL ON public.uploaded_files TO authenticated;
GRANT ALL ON public.test_connection TO authenticated;

-- Grant usage on uuid-ossp extension
GRANT ALL ON SCHEMA public TO authenticated;
-- Extension usage is automatically granted to users with schema privileges