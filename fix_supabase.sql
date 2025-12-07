-- AVALIA Code Analysis - Supabase Fix Script
-- Execute this to fix common errors

-- First, let's check what already exists
-- You can run these SELECT queries to check current state:

-- Check existing policies
SELECT schemaname, tablename, policyname
FROM pg_policies
WHERE schemaname = 'public';

-- Check existing tables
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;

-- Check if buckets exist (this might fail if you don't have access)
-- SELECT * FROM storage.buckets;

-- Fix for existing policies - we use IF NOT EXISTS or CREATE OR REPLACE
-- The original schema already created the policies, so we don't need to recreate them

-- Instead, let's verify our tables exist and have the correct structure
\d profiles
\d analyses
\d analysis_results
\d uploaded_files

-- Storage buckets need to be created via the Supabase Dashboard, not SQL
-- Go to: https://app.supabase.com/project/jjxmfidggofuaxcdtkrd/storage

-- Manual Storage Setup Instructions:
-- 1. Go to Storage section in Supabase Dashboard
-- 2. Create these buckets manually:
--    - code-files (private, 50MB)
--    - analysis-reports (private, 10MB)
--    - user-avatars (public, 5MB)

-- After creating buckets, you can set up Row Level Security policies via the dashboard

-- Test table access
SELECT COUNT(*) FROM profiles;
SELECT COUNT(*) FROM test_connection;