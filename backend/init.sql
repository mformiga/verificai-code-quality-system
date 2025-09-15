-- VerificAI Database Initialization Script

-- Create database if it doesn't exist
-- This is handled by Docker Compose environment variables

-- Create extensions for PostgreSQL
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create custom functions for better data handling
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create function to generate UUIDs
CREATE OR REPLACE FUNCTION generate_uuid()
RETURNS UUID AS $$
BEGIN
    RETURN uuid_generate_v4();
END;
$$ LANGUAGE plpgsql;

-- Create function to hash passwords
CREATE OR REPLACE FUNCTION hash_password(password TEXT)
RETURNS TEXT AS $$
BEGIN
    RETURN crypt(password, gen_salt('bf'));
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create trigger for updated_at timestamps
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_prompts_updated_at BEFORE UPDATE ON prompts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_analyses_updated_at BEFORE UPDATE ON analyses FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_analysis_results_updated_at BEFORE UPDATE ON analysis_results FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);
CREATE INDEX IF NOT EXISTS idx_prompts_author_id ON prompts(author_id);
CREATE INDEX IF NOT EXISTS idx_prompts_category ON prompts(category);
CREATE INDEX IF NOT EXISTS idx_prompts_status ON prompts(status);
CREATE INDEX IF NOT EXISTS idx_prompts_is_public ON prompts(is_public);
CREATE INDEX IF NOT EXISTS idx_analyses_user_id ON analyses(user_id);
CREATE INDEX IF NOT EXISTS idx_analyses_prompt_id ON analyses(prompt_id);
CREATE INDEX IF NOT EXISTS idx_analyses_status ON analyses(status);
CREATE INDEX IF NOT EXISTS idx_analyses_created_at ON analyses(created_at);
CREATE INDEX IF NOT EXISTS idx_analysis_results_analysis_id ON analysis_results(analysis_id);

-- Create full-text search indexes
CREATE INDEX IF NOT EXISTS idx_users_search ON users USING gin(to_tsvector('english', username || ' ' || email || ' ' || COALESCE(full_name, '')));
CREATE INDEX IF NOT EXISTS idx_prompts_search ON prompts USING gin(to_tsvector('english', name || ' ' || COALESCE(description, '')));
CREATE INDEX IF NOT EXISTS idx_analyses_search ON analyses USING gin(to_tsvector('english', name || ' ' || COALESCE(description, '')));

-- Create view for active users
CREATE OR REPLACE VIEW active_users AS
SELECT id, username, email, full_name, role, created_at, last_login
FROM users
WHERE is_active = true AND is_deleted = 0;

-- Create view for public prompts
CREATE OR REPLACE VIEW public_prompts AS
SELECT p.id, p.name, p.description, p.category, p.status, p.usage_count,
       p.success_rate, u.username as author_name, p.created_at
FROM prompts p
JOIN users u ON p.author_id = u.id
WHERE p.is_public = true AND p.status = 'active' AND p.is_deleted = 0
ORDER BY p.usage_count DESC, p.created_at DESC;

-- Create view for analysis statistics
CREATE OR REPLACE VIEW analysis_stats AS
SELECT
    COUNT(*) as total_analyses,
    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_analyses,
    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_analyses,
    COUNT(CASE WHEN status = 'processing' THEN 1 END) as processing_analyses,
    COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_analyses,
    AVG(CASE WHEN overall_score IS NOT NULL THEN overall_score END) as average_score,
    AVG(CASE WHEN security_score IS NOT NULL THEN security_score END) as average_security_score,
    AVG(CASE WHEN performance_score IS NOT NULL THEN performance_score END) as average_performance_score,
    AVG(CASE WHEN maintainability_score IS NOT NULL THEN maintainability_score END) as average_maintainability_score
FROM analyses
WHERE is_deleted = 0;

-- Create function to calculate user statistics
CREATE OR REPLACE FUNCTION get_user_stats(user_id INTEGER)
RETURNS TABLE(
    total_analyses INTEGER,
    completed_analyses INTEGER,
    failed_analyses INTEGER,
    average_score FLOAT,
    total_prompts INTEGER,
    public_prompts INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        COUNT(a.id)::INTEGER,
        COUNT(CASE WHEN a.status = 'completed' THEN 1 END)::INTEGER,
        COUNT(CASE WHEN a.status = 'failed' THEN 1 END)::INTEGER,
        AVG(CASE WHEN a.overall_score IS NOT NULL THEN a.overall_score END)::FLOAT,
        COUNT(p.id)::INTEGER,
        COUNT(CASE WHEN p.is_public = true THEN 1 END)::INTEGER
    FROM analyses a
    LEFT JOIN prompts p ON a.prompt_id = p.id
    WHERE a.user_id = get_user_stats.user_id
    AND a.is_deleted = 0;
END;
$$ LANGUAGE plpgsql;

-- Create function to cleanup old logs (can be scheduled)
CREATE OR REPLACE FUNCTION cleanup_old_logs(days_to_keep INTEGER DEFAULT 30)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM system_logs
    WHERE created_at < NOW() - INTERVAL '1 day' * days_to_keep;

    GET DIAGNOSTICS deleted_count = ROW_COUNT;

    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Create function to cleanup old failed analyses
CREATE OR REPLACE FUNCTION cleanup_old_failed_analyses(days_to_keep INTEGER DEFAULT 7)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM analyses
    WHERE status = 'failed'
    AND created_at < NOW() - INTERVAL '1 day' * days_to_keep
    AND is_deleted = 0;

    GET DIAGNOSTICS deleted_count = ROW_COUNT;

    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Grant permissions (adjust as needed)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO verificai;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO verificai;
-- GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO verificai;

-- Log initialization
INSERT INTO system_logs (level, message, created_at)
VALUES ('INFO', 'Database initialized successfully', NOW())
ON CONFLICT DO NOTHING;