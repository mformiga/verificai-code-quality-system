-- Create source_codes table in local PostgreSQL database
-- This table stores source code content directly as text

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Drop table if exists to start fresh (remove this line in production)
DROP TABLE IF EXISTS source_codes CASCADE;

-- Create source_codes table
CREATE TABLE source_codes (
    id SERIAL PRIMARY KEY,

    -- Basic identification
    code_id VARCHAR(255) UNIQUE NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,

    -- Source code content (main field - PostgreSQL TEXT supports up to 1GB)
    content TEXT NOT NULL,

    -- File information
    file_name VARCHAR(500) NOT NULL,
    file_extension VARCHAR(10) NOT NULL,
    programming_language VARCHAR(50),

    -- Code metrics
    line_count INTEGER,
    character_count INTEGER,
    size_bytes INTEGER,

    -- Content analysis
    language_detected VARCHAR(50),
    complexity_score VARCHAR(10),

    -- Classification and tagging
    category VARCHAR(100),
    tags TEXT, -- JSON array of tags
    metadata JSONB, -- Additional metadata

    -- Status and visibility
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'archived', 'deleted')),
    is_public BOOLEAN DEFAULT FALSE,
    is_template BOOLEAN DEFAULT FALSE,

    -- Processing information
    is_processed BOOLEAN DEFAULT FALSE,
    processing_status VARCHAR(50) DEFAULT 'pending',
    processing_error TEXT,

    -- Analysis information
    analysis_id VARCHAR(255),
    last_analyzed_at TIMESTAMP WITH TIME ZONE,

    -- Ownership and access (will connect to users table when ready)
    user_id INTEGER, -- References users.id when user system is integrated
    access_level VARCHAR(20) DEFAULT 'private' CHECK (access_level IN ('private', 'team', 'public')),

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_source_codes_code_id ON source_codes(code_id);
CREATE INDEX idx_source_codes_user_id ON source_codes(user_id);
CREATE INDEX idx_source_codes_status ON source_codes(status);
CREATE INDEX idx_source_codes_programming_language ON source_codes(programming_language);
CREATE INDEX idx_source_codes_file_extension ON source_codes(file_extension);
CREATE INDEX idx_source_codes_created_at ON source_codes(created_at);
CREATE INDEX idx_source_codes_is_processed ON source_codes(is_processed);

-- Create GIN index for JSONB metadata
CREATE INDEX idx_source_codes_metadata_gin ON source_codes USING GIN(metadata);

-- Create trigger to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_source_codes_updated_at
    BEFORE UPDATE ON source_codes
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Add comments for documentation
COMMENT ON TABLE source_codes IS 'Stores source code content directly as text with metadata and analysis status';
COMMENT ON COLUMN source_codes.code_id IS 'Unique identifier for the source code entry';
COMMENT ON COLUMN source_codes.content IS 'Source code content - PostgreSQL TEXT supports up to 1GB';
COMMENT ON COLUMN source_codes.file_extension IS 'File extension for language detection (.py, .js, etc.)';
COMMENT ON COLUMN source_codes.programming_language IS 'Detected or specified programming language';
COMMENT ON COLUMN source_codes.line_count IS 'Number of lines in the source code';
COMMENT ON COLUMN source_codes.character_count IS 'Total character count';
COMMENT ON COLUMN source_codes.size_bytes IS 'Size in bytes of the content';
COMMENT ON COLUMN source_codes.status IS 'Current status: active, archived, deleted';
COMMENT ON COLUMN source_codes.is_processed IS 'Whether the code has been processed for analysis';
COMMENT ON COLUMN source_codes.processing_status IS 'Processing status: pending, processing, completed, error';
COMMENT ON COLUMN source_codes.tags IS 'JSON array of tags for categorization';
COMMENT ON COLUMN source_codes.metadata IS 'Additional metadata stored as JSON';

-- Grant permissions (adjust username as needed)
-- GRANT ALL PRIVILEGES ON TABLE source_codes TO verificai_user;
-- GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO verificai_user;