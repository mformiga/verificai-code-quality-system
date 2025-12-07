-- Create source_codes table in Supabase with exact structure requested
-- This script creates the table with UUID primary key and auth.users reference

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Drop table if exists (remove this line in production)
-- DROP TABLE IF EXISTS source_codes CASCADE;

-- Create source_codes table with exact structure requested
CREATE TABLE public.source_codes (
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
    user_id UUID REFERENCES auth.users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes
CREATE INDEX idx_source_codes_code_id ON source_codes(code_id);
CREATE INDEX idx_source_codes_status ON source_codes(status);
CREATE INDEX idx_source_codes_user_id ON source_codes(user_id);

-- Create trigger for updated_at
CREATE OR REPLACE FUNCTION update_source_codes_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_source_codes_updated_at
BEFORE UPDATE ON source_codes
FOR EACH ROW EXECUTE FUNCTION update_source_codes_updated_at();

-- Enable Row Level Security (RLS)
ALTER TABLE source_codes ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
-- Users can view their own source codes
CREATE POLICY "Users can view own source codes" ON source_codes
    FOR SELECT USING (auth.uid() = user_id);

-- Users can insert their own source codes
CREATE POLICY "Users can insert own source codes" ON source_codes
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Users can update their own source codes
CREATE POLICY "Users can update own source codes" ON source_codes
    FOR UPDATE USING (auth.uid() = user_id);

-- Users can delete their own source codes
CREATE POLICY "Users can delete own source codes" ON source_codes
    FOR DELETE USING (auth.uid() = user_id);

-- Public can view public source codes
CREATE POLICY "Public source codes are viewable by everyone" ON source_codes
    FOR SELECT USING (is_public = true);

-- Add comments for documentation
COMMENT ON TABLE source_codes IS 'Stores source code content with metadata and processing status';
COMMENT ON COLUMN source_codes.code_id IS 'Unique identifier for the source code entry';
COMMENT ON COLUMN source_codes.content IS 'Source code content';
COMMENT ON COLUMN source_codes.file_extension IS 'File extension for language detection';
COMMENT ON COLUMN source_codes.programming_language IS 'Detected or specified programming language';
COMMENT ON COLUMN source_codes.line_count IS 'Number of lines in the source code';
COMMENT ON COLUMN source_codes.character_count IS 'Total character count';
COMMENT ON COLUMN source_codes.size_bytes IS 'Size in bytes of the content';
COMMENT ON COLUMN source_codes.status IS 'Current status';
COMMENT ON COLUMN source_codes.is_processed IS 'Whether the code has been processed for analysis';
COMMENT ON COLUMN source_codes.processing_status IS 'Processing status: pending, processing, completed, error';
COMMENT ON COLUMN source_codes.user_id IS 'Reference to auth.users table';