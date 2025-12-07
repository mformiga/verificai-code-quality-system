-- ===============================================================
-- SUPABASE COMPLETE DDL FOR AVALIA CODE ANALYSIS SYSTEM
-- Project: jjxmfidggofuaxcdtkrd
-- Execute this script in Supabase SQL Editor
-- ===============================================================

-- 1. Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 2. Create source_codes table (if not exists)
CREATE TABLE IF NOT EXISTS public.source_codes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code_id VARCHAR(255) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    content TEXT NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_extension VARCHAR(50) NOT NULL,
    programming_language VARCHAR(100),
    line_count INTEGER,
    character_count INTEGER,
    size_bytes BIGINT,
    status VARCHAR(50) DEFAULT 'active',
    is_public BOOLEAN DEFAULT false,
    is_processed BOOLEAN DEFAULT false,
    processing_status VARCHAR(50) DEFAULT 'pending',
    user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Create indexes for source_codes
CREATE INDEX IF NOT EXISTS idx_source_codes_code_id ON public.source_codes(code_id);
CREATE INDEX IF NOT EXISTS idx_source_codes_status ON public.source_codes(status);
CREATE INDEX IF NOT EXISTS idx_source_codes_user_id ON public.source_codes(user_id);
CREATE INDEX IF NOT EXISTS idx_source_codes_created_at ON public.source_codes(created_at DESC);

-- 4. Create function for updated_at trigger
CREATE OR REPLACE FUNCTION public.update_source_codes_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 5. Create trigger for source_codes
DROP TRIGGER IF EXISTS update_source_codes_updated_at ON public.source_codes;
CREATE TRIGGER update_source_codes_updated_at
    BEFORE UPDATE ON public.source_codes
    FOR EACH ROW
    EXECUTE FUNCTION public.update_source_codes_updated_at();

-- 6. Enable Row Level Security (RLS) for source_codes
ALTER TABLE public.source_codes ENABLE ROW LEVEL SECURITY;

-- 7. Create RLS policies for source_codes
-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Users can view own source codes" ON public.source_codes;
DROP POLICY IF EXISTS "Users can insert own source codes" ON public.source_codes;
DROP POLICY IF EXISTS "Users can update own source codes" ON public.source_codes;
DROP POLICY IF EXISTS "Users can delete own source codes" ON public.source_codes;
DROP POLICY IF EXISTS "Public source codes are viewable by everyone" ON public.source_codes;

-- Create new policies
CREATE POLICY "Users can view own source codes" ON public.source_codes
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own source codes" ON public.source_codes
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own source codes" ON public.source_codes
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own source codes" ON public.source_codes
    FOR DELETE USING (auth.uid() = user_id);

CREATE POLICY "Public source codes are viewable by everyone" ON public.source_codes
    FOR SELECT USING (is_public = true);

-- 8. Update existing prompt_configurations (add missing columns if needed)
ALTER TABLE public.prompt_configurations
ADD COLUMN IF NOT EXISTS code_id VARCHAR(255),
ADD COLUMN IF NOT EXISTS file_name VARCHAR(255),
ADD COLUMN IF NOT EXISTS file_extension VARCHAR(50),
ADD COLUMN IF NOT EXISTS programming_language VARCHAR(100),
ADD COLUMN IF NOT EXISTS line_count INTEGER,
ADD COLUMN IF NOT EXISTS character_count INTEGER,
ADD COLUMN IF NOT EXISTS size_bytes BIGINT;

-- 9. Ensure prompt_configurations has proper indexes
CREATE INDEX IF NOT EXISTS idx_prompt_configurations_type ON public.prompt_configurations(prompt_type);
CREATE INDEX IF NOT EXISTS idx_prompt_configurations_active ON public.prompt_configurations(is_active);
CREATE INDEX IF NOT EXISTS idx_prompt_configurations_updated_at ON public.prompt_configurations(updated_at DESC);

-- 10. Create updated_at trigger for prompt_configurations
CREATE OR REPLACE FUNCTION public.update_prompt_configurations_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_prompt_configurations_updated_at ON public.prompt_configurations;
CREATE TRIGGER update_prompt_configurations_updated_at
    BEFORE UPDATE ON public.prompt_configurations
    FOR EACH ROW
    EXECUTE FUNCTION public.update_prompt_configurations_updated_at();

-- 11. Enable RLS for prompt_configurations (if not already enabled)
ALTER TABLE public.prompt_configurations ENABLE ROW LEVEL SECURITY;

-- 12. Create RLS policies for prompt_configurations
-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Users can view all prompt configurations" ON public.prompt_configurations;
DROP POLICY IF EXISTS "Users can insert prompt configurations" ON public.prompt_configurations;
DROP POLICY IF EXISTS "Users can update own prompt configurations" ON public.prompt_configurations;

-- Create new policies (more permissive for system functionality)
CREATE POLICY "Users can view all prompt configurations" ON public.prompt_configurations
    FOR SELECT USING (true);

CREATE POLICY "Users can insert prompt configurations" ON public.prompt_configurations
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Users can update own prompt configurations" ON public.prompt_configurations
    FOR UPDATE USING (created_by = auth.uid() OR created_by IS NULL);

-- 13. Add table comments for documentation
COMMENT ON TABLE public.source_codes IS 'Stores source code content with metadata and processing status for AVALIA code analysis system';
COMMENT ON TABLE public.prompt_configurations IS 'Configuration templates for different types of code analysis prompts';

-- 14. Create storage bucket for code files (if needed)
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
    'source-code-files',
    'source-code-files',
    false,  -- Private bucket
    50 * 1024 * 1024,  -- 50MB limit
    ARRAY[
        'text/plain', 'text/html', 'text/css', 'text/javascript', 'application/javascript',
        'application/json', 'application/xml', 'text/xml', 'text/x-python',
        'text/x-java-source', 'text/x-c', 'text/x-c++src', 'application/x-sh',
        'text/markdown', 'text/x-sql', 'application/vnd.ms.portable-executable'
    ]
)
ON CONFLICT (id) DO NOTHING;

-- 15. Create storage policies for the bucket
-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Users can upload source code files" ON storage.objects;
DROP POLICY IF EXISTS "Users can view own source code files" ON storage.objects;

-- Create new storage policies
CREATE POLICY "Users can upload source code files" ON storage.objects
    FOR INSERT WITH CHECK (
        bucket_id = 'source-code-files' AND
        (storage.foldername(name))[1] = auth.uid()::text
    );

CREATE POLICY "Users can view own source code files" ON storage.objects
    FOR SELECT USING (
        bucket_id = 'source-code-files' AND
        (storage.foldername(name))[1] = auth.uid()::text
    );

-- ===============================================================
-- VERIFICATION QUERIES
-- Run these after execution to verify everything was created
-- ===============================================================

-- Verify tables exist
SELECT
    schemaname,
    tablename,
    tableowner
FROM pg_tables
WHERE schemaname = 'public'
    AND tablename IN ('source_codes', 'prompt_configurations')
ORDER BY tablename;

-- Verify indexes
SELECT
    indexname,
    tablename,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
    AND tablename IN ('source_codes', 'prompt_configurations')
ORDER BY tablename, indexname;

-- Verify RLS is enabled
SELECT
    schemaname,
    tablename,
    rowsecurity
FROM pg_tables
WHERE schemaname = 'public'
    AND tablename IN ('source_codes', 'prompt_configurations')
ORDER BY tablename;

-- Verify RLS policies
SELECT
    schemaname,
    tablename,
    policyname,
    permissive,
    roles,
    cmd,
    qual
FROM pg_policies
WHERE schemaname = 'public'
    AND tablename IN ('source_codes', 'prompt_configurations')
ORDER BY tablename, policyname;

-- ===============================================================
-- SAMPLE INSERT (optional - for testing)
-- Uncomment to insert test data
-- ===============================================================

-- INSERT INTO public.source_codes (
--     code_id,
--     title,
--     description,
--     content,
--     file_name,
--     file_extension,
--     programming_language,
--     line_count,
--     character_count,
--     size_bytes
-- ) VALUES (
--     'test_example_001',
--     'Example Function',
--     'A simple test function',
--     'def hello_world():\n    print("Hello, World!")\n    return True',
--     'hello.py',
--     '.py',
--     'Python',
--     3,
--     67,
--     67
-- );

-- ===============================================================
-- COMPLETION MESSAGE
-- ===============================================================

DO $$
BEGIN
    RAISE NOTICE '===========================================';
    RAISE NOTICE 'AVALIA CODE ANALYSIS SYSTEM - SETUP COMPLETE';
    RAISE NOTICE 'Tables created: source_codes, prompt_configurations';
    RAISE NOTICE 'RLS enabled with appropriate policies';
    RAISE NOTICE 'Indexes created for performance';
    RAISE NOTICE 'Storage bucket created: source-code-files';
    RAISE NOTICE 'Ready for Streamlit Cloud deployment!';
    RAISE NOTICE '===========================================';
END $$;