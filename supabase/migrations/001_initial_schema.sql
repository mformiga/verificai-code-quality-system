-- AVALIA Code Analysis Application - Initial Database Schema
-- This migration creates all necessary tables for the AVALIA application

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create custom enums
CREATE TYPE user_role AS ENUM ('ADMIN', 'QA_ENGINEER', 'DEVELOPER', 'VIEWER');
CREATE TYPE analysis_status AS ENUM ('pending', 'processing', 'completed', 'failed', 'cancelled');
CREATE TYPE prompt_type AS ENUM ('general', 'architectural', 'business');
CREATE TYPE prompt_category AS ENUM ('code_analysis', 'architecture', 'business', 'quality', 'security', 'performance', 'testing', 'documentation');
CREATE TYPE prompt_status AS ENUM ('active', 'inactive', 'draft', 'archived', 'deprecated');
CREATE TYPE file_status AS ENUM ('uploading', 'completed', 'error', 'deleted');

-- Users table (extends Supabase auth.users)
CREATE TABLE public.profiles (
    id uuid REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
    username text UNIQUE NOT NULL,
    email text UNIQUE NOT NULL,
    full_name text,
    is_active boolean DEFAULT true NOT NULL,
    is_verified boolean DEFAULT false NOT NULL,
    role user_role DEFAULT 'QA_ENGINEER' NOT NULL,
    is_admin boolean DEFAULT false NOT NULL,

    -- Profile information
    bio text,
    avatar_url text,

    -- Preferences
    preferred_language text DEFAULT 'en',
    timezone text DEFAULT 'UTC',

    -- Security
    last_login timestamptz,
    password_changed_at timestamptz,
    failed_login_attempts integer DEFAULT 0,
    locked_until timestamptz,

    -- Email preferences
    email_notifications boolean DEFAULT true NOT NULL,
    email_analysis_reports boolean DEFAULT true NOT NULL,
    email_security_alerts boolean DEFAULT true NOT NULL,

    -- Metadata
    created_at timestamptz DEFAULT now() NOT NULL,
    updated_at timestamptz DEFAULT now() NOT NULL
);

-- Prompts table for storing analysis prompts
CREATE TABLE public.prompts (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id uuid REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL,
    type prompt_type NOT NULL UNIQUE,
    content text NOT NULL,
    version integer DEFAULT 1 NOT NULL,
    status prompt_status DEFAULT 'active' NOT NULL,
    category prompt_category DEFAULT 'code_analysis' NOT NULL,
    name text NOT NULL,
    description text,

    -- Metadata
    created_at timestamptz DEFAULT now() NOT NULL,
    updated_at timestamptz DEFAULT now() NOT NULL
);

-- Prompt history table for version control
CREATE TABLE public.prompt_history (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    prompt_id uuid REFERENCES public.prompts(id) ON DELETE CASCADE NOT NULL,
    version integer NOT NULL,
    content text NOT NULL,

    -- Metadata
    created_at timestamptz DEFAULT now() NOT NULL,

    UNIQUE(prompt_id, version)
);

-- Prompt configurations table for user-specific settings
CREATE TABLE public.prompt_configurations (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id uuid REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL,
    prompt_type prompt_type NOT NULL,
    name text NOT NULL,
    description text,
    content text NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    is_default boolean DEFAULT false NOT NULL,
    settings jsonb,

    -- Metadata
    created_at timestamptz DEFAULT now() NOT NULL,
    updated_at timestamptz DEFAULT now() NOT NULL,

    UNIQUE(user_id, name),
    UNIQUE(user_id, prompt_type)
);

-- General criteria table for user-defined analysis criteria
CREATE TABLE public.general_criteria (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id uuid REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL,
    text text NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    "order" integer DEFAULT 0 NOT NULL,

    -- Metadata
    created_at timestamptz DEFAULT now() NOT NULL,
    updated_at timestamptz DEFAULT now() NOT NULL,

    UNIQUE(user_id, text)
);

-- Analyses table for tracking code analysis jobs
CREATE TABLE public.analyses (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    name text NOT NULL,
    description text,
    status analysis_status DEFAULT 'pending' NOT NULL,

    -- Foreign keys
    user_id uuid REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL,
    prompt_id uuid REFERENCES public.prompts(id) ON DELETE CASCADE NOT NULL,

    -- Input data
    repository_url text,
    file_paths text, -- JSON array of file paths
    code_content text,
    configuration jsonb,

    -- Processing information
    started_at timestamptz,
    completed_at timestamptz,
    error_message text,
    progress_percentage integer DEFAULT 0 NOT NULL,

    -- Metadata
    language text,
    total_files integer DEFAULT 0 NOT NULL,
    total_lines integer DEFAULT 0 NOT NULL,
    file_size_bytes bigint DEFAULT 0 NOT NULL,

    -- Results summary
    total_issues integer DEFAULT 0 NOT NULL,
    critical_issues integer DEFAULT 0 NOT NULL,
    warning_issues integer DEFAULT 0 NOT NULL,
    info_issues integer DEFAULT 0 NOT NULL,

    -- Quality scores
    overall_score integer,
    security_score integer,
    performance_score integer,
    maintainability_score integer,

    -- AI model information
    model_used text,
    tokens_used integer,
    processing_time text,

    -- Cost tracking
    estimated_cost text,
    actual_cost text,

    -- Timestamps
    created_at timestamptz DEFAULT now() NOT NULL,
    updated_at timestamptz DEFAULT now() NOT NULL
);

-- Analysis results table for detailed results
CREATE TABLE public.analysis_results (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    analysis_id uuid REFERENCES public.analyses(id) ON DELETE CASCADE NOT NULL UNIQUE,

    -- Results data
    summary text NOT NULL,
    detailed_findings text,
    recommendations text,
    score integer,
    confidence text,

    -- Detailed analysis data (JSON)
    issues jsonb,
    metrics jsonb,
    code_snippets jsonb,
    file_analysis jsonb,

    -- AI model information
    model_used text,
    tokens_used integer,
    processing_time text,

    -- Quality indicators
    quality_score integer,
    security_score integer,
    performance_score integer,
    maintainability_score integer,

    -- Metadata
    created_at timestamptz DEFAULT now() NOT NULL,
    updated_at timestamptz DEFAULT now() NOT NULL
);

-- General analysis results table
CREATE TABLE public.general_analysis_results (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,

    -- Analysis metadata
    analysis_name text NOT NULL,
    criteria_count integer NOT NULL,

    -- Foreign key
    user_id uuid REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL,

    -- Analysis results (JSON format)
    criteria_results jsonb NOT NULL,
    raw_response text NOT NULL,

    -- Model information
    model_used text,
    usage jsonb,

    -- Input data for reference
    file_paths text,
    modified_prompt text,

    -- Processing info
    processing_time text,

    -- Metadata
    created_at timestamptz DEFAULT now() NOT NULL,
    updated_at timestamptz DEFAULT now() NOT NULL
);

-- Uploaded files table
CREATE TABLE public.uploaded_files (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,

    -- Basic information
    file_id text UNIQUE NOT NULL,
    original_name text NOT NULL,
    file_path text NOT NULL,
    relative_path text,
    file_size integer NOT NULL,
    mime_type text,
    file_extension text,

    -- Storage information
    storage_path text NOT NULL,
    checksum text,
    is_compressed boolean DEFAULT false NOT NULL,

    -- Upload status
    status file_status DEFAULT 'uploading' NOT NULL,
    upload_progress integer DEFAULT 0 NOT NULL,
    error_message text,

    -- File processing status
    is_processed boolean DEFAULT false NOT NULL,
    processing_status text,
    processing_error text,

    -- Analysis information
    analysis_id text,
    language_detected text,
    line_count integer,
    complexity_score text,

    -- Metadata
    file_metadata jsonb,
    tags text, -- JSON array of tags

    -- Ownership and access
    user_id uuid REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL,
    is_public boolean DEFAULT false NOT NULL,
    access_level text DEFAULT 'private' NOT NULL,

    -- Timestamps
    created_at timestamptz DEFAULT now() NOT NULL,
    updated_at timestamptz DEFAULT now() NOT NULL
);

-- Create indexes for better performance
CREATE INDEX idx_profiles_username ON public.profiles(username);
CREATE INDEX idx_profiles_email ON public.profiles(email);
CREATE INDEX idx_profiles_role ON public.profiles(role);
CREATE INDEX idx_prompts_type ON public.prompts(type);
CREATE INDEX idx_prompts_user_id ON public.prompts(user_id);
CREATE INDEX idx_analyses_user_id ON public.analyses(user_id);
CREATE INDEX idx_analyses_status ON public.analyses(status);
CREATE INDEX idx_analyses_created_at ON public.analyses(created_at);
CREATE INDEX idx_uploaded_files_user_id ON public.uploaded_files(user_id);
CREATE INDEX idx_uploaded_files_status ON public.uploaded_files(status);
CREATE INDEX idx_uploaded_files_file_id ON public.uploaded_files(file_id);
CREATE INDEX idx_general_criteria_user_id ON public.general_criteria(user_id);
CREATE INDEX idx_general_criteria_is_active ON public.general_criteria(is_active);

-- Enable Row Level Security on all tables
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.prompts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.prompt_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.prompt_configurations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.general_criteria ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.analysis_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.general_analysis_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.uploaded_files ENABLE ROW LEVEL SECURITY;

-- RLS Policies for profiles table
CREATE POLICY "Users can view own profile" ON public.profiles FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can update own profile" ON public.profiles FOR UPDATE USING (auth.uid() = id);
CREATE POLICY "Admins can view all profiles" ON public.profiles FOR SELECT USING (
    EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND is_admin = true)
);
CREATE POLICY "Admins can update all profiles" ON public.profiles FOR UPDATE USING (
    EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND is_admin = true)
);
CREATE POLICY "Users can insert own profile" ON public.profiles FOR INSERT WITH CHECK (auth.uid() = id);

-- RLS Policies for prompts table
CREATE POLICY "Users can view prompts" ON public.prompts FOR SELECT USING (true);
CREATE POLICY "Admins can insert prompts" ON public.prompts FOR INSERT WITH CHECK (
    EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND is_admin = true)
);
CREATE POLICY "Admins can update prompts" ON public.prompts FOR UPDATE USING (
    EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND is_admin = true)
);
CREATE POLICY "Admins can delete prompts" ON public.prompts FOR DELETE USING (
    EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND is_admin = true)
);

-- RLS Policies for prompt_configurations table
CREATE POLICY "Users can view own prompt configurations" ON public.prompt_configurations FOR SELECT USING (user_id = auth.uid());
CREATE POLICY "Users can insert own prompt configurations" ON public.prompt_configurations FOR INSERT WITH CHECK (user_id = auth.uid());
CREATE POLICY "Users can update own prompt configurations" ON public.prompt_configurations FOR UPDATE USING (user_id = auth.uid());
CREATE POLICY "Users can delete own prompt configurations" ON public.prompt_configurations FOR DELETE USING (user_id = auth.uid());

-- RLS Policies for general_criteria table
CREATE POLICY "Users can view own criteria" ON public.general_criteria FOR SELECT USING (user_id = auth.uid());
CREATE POLICY "Users can insert own criteria" ON public.general_criteria FOR INSERT WITH CHECK (user_id = auth.uid());
CREATE POLICY "Users can update own criteria" ON public.general_criteria FOR UPDATE USING (user_id = auth.uid());
CREATE POLICY "Users can delete own criteria" ON public.general_criteria FOR DELETE USING (user_id = auth.uid());

-- RLS Policies for analyses table
CREATE POLICY "Users can view own analyses" ON public.analyses FOR SELECT USING (user_id = auth.uid());
CREATE POLICY "Users can insert own analyses" ON public.analyses FOR INSERT WITH CHECK (user_id = auth.uid());
CREATE POLICY "Users can update own analyses" ON public.analyses FOR UPDATE USING (user_id = auth.uid());
CREATE POLICY "Admins can view all analyses" ON public.analyses FOR SELECT USING (
    EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND is_admin = true)
);

-- RLS Policies for analysis_results table
CREATE POLICY "Users can view own analysis results" ON public.analysis_results FOR SELECT USING (
    EXISTS (SELECT 1 FROM public.analyses WHERE id = analysis_id AND user_id = auth.uid())
);
CREATE POLICY "Users can insert own analysis results" ON public.analysis_results FOR INSERT WITH CHECK (
    EXISTS (SELECT 1 FROM public.analyses WHERE id = analysis_id AND user_id = auth.uid())
);
CREATE POLICY "Users can update own analysis results" ON public.analysis_results FOR UPDATE USING (
    EXISTS (SELECT 1 FROM public.analyses WHERE id = analysis_id AND user_id = auth.uid())
);
CREATE POLICY "Admins can view all analysis results" ON public.analysis_results FOR SELECT USING (
    EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND is_admin = true)
);

-- RLS Policies for general_analysis_results table
CREATE POLICY "Users can view own general analysis results" ON public.general_analysis_results FOR SELECT USING (user_id = auth.uid());
CREATE POLICY "Users can insert own general analysis results" ON public.general_analysis_results FOR INSERT WITH CHECK (user_id = auth.uid());
CREATE POLICY "Users can update own general analysis results" ON public.general_analysis_results FOR UPDATE USING (user_id = auth.uid());
CREATE POLICY "Admins can view all general analysis results" ON public.general_analysis_results FOR SELECT USING (
    EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND is_admin = true)
);

-- RLS Policies for uploaded_files table
CREATE POLICY "Users can view own files" ON public.uploaded_files FOR SELECT USING (user_id = auth.uid());
CREATE POLICY "Users can insert own files" ON public.uploaded_files FOR INSERT WITH CHECK (user_id = auth.uid());
CREATE POLICY "Users can update own files" ON public.uploaded_files FOR UPDATE USING (user_id = auth.uid());
CREATE POLICY "Users can delete own files" ON public.uploaded_files FOR DELETE USING (user_id = auth.uid());
CREATE POLICY "Public access to public files" ON public.uploaded_files FOR SELECT USING (is_public = true);

-- RLS Policies for prompt_history table
CREATE POLICY "Users can view prompt history" ON public.prompt_history FOR SELECT USING (true);
CREATE POLICY "Admins can manage prompt history" ON public.prompt_history FOR ALL USING (
    EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND is_admin = true)
);

-- Create triggers for updated_at timestamps
CREATE OR REPLACE FUNCTION public.handle_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER handle_profiles_updated_at
    BEFORE UPDATE ON public.profiles
    FOR EACH ROW EXECUTE FUNCTION public.handle_updated_at();

CREATE TRIGGER handle_prompts_updated_at
    BEFORE UPDATE ON public.prompts
    FOR EACH ROW EXECUTE FUNCTION public.handle_updated_at();

CREATE TRIGGER handle_prompt_configurations_updated_at
    BEFORE UPDATE ON public.prompt_configurations
    FOR EACH ROW EXECUTE FUNCTION public.handle_updated_at();

CREATE TRIGGER handle_general_criteria_updated_at
    BEFORE UPDATE ON public.general_criteria
    FOR EACH ROW EXECUTE FUNCTION public.handle_updated_at();

CREATE TRIGGER handle_analyses_updated_at
    BEFORE UPDATE ON public.analyses
    FOR EACH ROW EXECUTE FUNCTION public.handle_updated_at();

CREATE TRIGGER handle_analysis_results_updated_at
    BEFORE UPDATE ON public.analysis_results
    FOR EACH ROW EXECUTE FUNCTION public.handle_updated_at();

CREATE TRIGGER handle_general_analysis_results_updated_at
    BEFORE UPDATE ON public.general_analysis_results
    FOR EACH ROW EXECUTE FUNCTION public.handle_updated_at();

CREATE TRIGGER handle_uploaded_files_updated_at
    BEFORE UPDATE ON public.uploaded_files
    FOR EACH ROW EXECUTE FUNCTION public.handle_updated_at();

-- Create function to handle new user registration
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, username, email)
    VALUES (NEW.id, NEW.email, NEW.email);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create trigger for new user registration
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();