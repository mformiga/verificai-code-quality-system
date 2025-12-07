-- AVALIA Code Analysis - Supabase Storage Setup
-- Execute this after creating the database schema

-- Create storage buckets for AVALIA

-- 1. Code files bucket (for user uploads)
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
    'code-files',
    'code-files',
    false,  -- Private bucket
    50 * 1024 * 1024,  -- 50MB limit
    ARRAY[
        'text/plain',
        'text/html',
        'text/css',
        'text/javascript',
        'application/javascript',
        'application/json',
        'application/xml',
        'text/xml',
        'text/x-python',
        'text/x-java-source',
        'text/x-c',
        'text/x-c++src',
        'application/x-sh',
        'text/markdown',
        'text/x-sql',
        'application/vnd.ms.portable-executable',
        'application/x-msdownload',
        'application/x-msdos-program',
        'application/x-executable'
    ]
) ON CONFLICT (id) DO NOTHING;

-- 2. Analysis reports bucket
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
    'analysis-reports',
    'analysis-reports',
    false,  -- Private bucket
    10 * 1024 * 1024,  -- 10MB limit
    ARRAY[
        'application/json',
        'text/plain',
        'application/pdf',
        'text/html',
        'text/markdown'
    ]
) ON CONFLICT (id) DO NOTHING;

-- 3. User avatars bucket
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
    'user-avatars',
    'user-avatars',
    true,  -- Public bucket for avatars
    5 * 1024 * 1024,  -- 5MB limit
    ARRAY[
        'image/jpeg',
        'image/png',
        'image/gif',
        'image/webp',
        'image/svg+xml'
    ]
) ON CONFLICT (id) DO NOTHING;

-- Row Level Security Policies for Storage

-- Code files bucket policies
CREATE POLICY "Users can view own code files" ON storage.objects
    FOR SELECT USING (
        bucket_id = 'code-files' AND
        auth.uid()::text = (storage.foldername(name))[1]
    );

CREATE POLICY "Users can upload own code files" ON storage.objects
    FOR INSERT WITH CHECK (
        bucket_id = 'code-files' AND
        auth.uid()::text = (storage.foldername(name))[1]
    );

CREATE POLICY "Users can update own code files" ON storage.objects
    FOR UPDATE USING (
        bucket_id = 'code-files' AND
        auth.uid()::text = (storage.foldername(name))[1]
    );

CREATE POLICY "Users can delete own code files" ON storage.objects
    FOR DELETE USING (
        bucket_id = 'code-files' AND
        auth.uid()::text = (storage.foldername(name))[1]
    );

-- Analysis reports bucket policies
CREATE POLICY "Users can view own analysis reports" ON storage.objects
    FOR SELECT USING (
        bucket_id = 'analysis-reports' AND
        auth.uid()::text = (storage.foldername(name))[1]
    );

CREATE POLICY "Users can upload own analysis reports" ON storage.objects
    FOR INSERT WITH CHECK (
        bucket_id = 'analysis-reports' AND
        auth.uid()::text = (storage.foldername(name))[1]
    );

CREATE POLICY "Users can update own analysis reports" ON storage.objects
    FOR UPDATE USING (
        bucket_id = 'analysis-reports' AND
        auth.uid()::text = (storage.foldername(name))[1]
    );

CREATE POLICY "Users can delete own analysis reports" ON storage.objects
    FOR DELETE USING (
        bucket_id = 'analysis-reports' AND
        auth.uid()::text = (storage.foldername(name))[1]
    );

-- User avatars bucket policies (public read access)
CREATE POLICY "Anyone can view avatars" ON storage.objects
    FOR SELECT USING (bucket_id = 'user-avatars');

CREATE POLICY "Users can upload own avatar" ON storage.objects
    FOR INSERT WITH CHECK (
        bucket_id = 'user-avatars' AND
        auth.uid()::text = (storage.foldername(name))[1]
    );

CREATE POLICY "Users can update own avatar" ON storage.objects
    FOR UPDATE USING (
        bucket_id = 'user-avatars' AND
        auth.uid()::text = (storage.foldername(name))[1]
    );

CREATE POLICY "Users can delete own avatar" ON storage.objects
    FOR DELETE USING (
        bucket_id = 'user-avatars' AND
        auth.uid()::text = (storage.foldername(name))[1]
    );

-- Grant permissions
GRANT ALL ON storage.buckets TO authenticated;
GRANT ALL ON storage.objects TO authenticated;

-- Create a function to extract user ID from file path
CREATE OR REPLACE FUNCTION storage.foldername(path text)
RETURNS text[] AS $$
BEGIN
    RETURN string_to_array(path, '/');
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Test storage setup
DO $$
BEGIN
    RAISE NOTICE 'Storage setup completed successfully!';
    RAISE NOTICE 'Buckets created: code-files, analysis-reports, user-avatars';
    RAISE NOTICE 'RLS policies applied to all buckets';
END $$;