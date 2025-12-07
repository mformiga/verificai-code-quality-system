-- =================================================================
-- CRIAÇÃO DA TABELA SOURCE_CODES NO SUPABASE
-- Execute este script no SQL Editor do painel do Supabase
-- Projeto: https://app.supabase.com/project/jjxmfidggofuaxcdtkrd
-- =================================================================

-- 1. Criar extensão UUID (se ainda não existir)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 2. Criar a tabela source_codes
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
    user_id UUID REFERENCES auth.users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Criar índices para melhor performance
CREATE INDEX IF NOT EXISTS idx_source_codes_code_id ON source_codes(code_id);
CREATE INDEX IF NOT EXISTS idx_source_codes_status ON source_codes(status);
CREATE INDEX IF NOT EXISTS idx_source_codes_user_id ON source_codes(user_id);

-- 4. Criar função para atualizar automaticamente o campo updated_at
CREATE OR REPLACE FUNCTION update_source_codes_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 5. Criar trigger que dispara a função antes de atualizações
DROP TRIGGER IF EXISTS update_source_codes_updated_at ON source_codes;
CREATE TRIGGER update_source_codes_updated_at
BEFORE UPDATE ON source_codes
FOR EACH ROW EXECUTE FUNCTION update_source_codes_updated_at();

-- 6. Habilitar Row Level Security (RLS) para segurança
ALTER TABLE source_codes ENABLE ROW LEVEL SECURITY;

-- 7. Remover políticas existentes (se houver) para evitar conflitos
DROP POLICY IF EXISTS "Users can view own source codes" ON source_codes;
DROP POLICY IF EXISTS "Users can insert own source codes" ON source_codes;
DROP POLICY IF EXISTS "Users can update own source codes" ON source_codes;
DROP POLICY IF EXISTS "Users can delete own source codes" ON source_codes;
DROP POLICY IF EXISTS "Public source codes are viewable by everyone" ON source_codes;

-- 8. Criar políticas de segurança (RLS)
-- Usuários podem ver seus próprios códigos
CREATE POLICY "Users can view own source codes" ON source_codes
    FOR SELECT USING (auth.uid() = user_id);

-- Usuários podem inserir seus próprios códigos
CREATE POLICY "Users can insert own source codes" ON source_codes
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Usuários podem atualizar seus próprios códigos
CREATE POLICY "Users can update own source codes" ON source_codes
    FOR UPDATE USING (auth.uid() = user_id);

-- Usuários podem deletar seus próprios códigos
CREATE POLICY "Users can delete own source codes" ON source_codes
    FOR DELETE USING (auth.uid() = user_id);

-- Códigos públicos podem ser vistos por qualquer pessoa
CREATE POLICY "Public source codes are viewable by everyone" ON source_codes
    FOR SELECT USING (is_public = true);

-- 9. Adicionar comentários para documentação
COMMENT ON TABLE source_codes IS 'Stores source code content with metadata and processing status';
COMMENT ON COLUMN source_codes.id IS 'Primary key - UUID generated automatically';
COMMENT ON COLUMN source_codes.code_id IS 'Unique identifier for the source code entry';
COMMENT ON COLUMN source_codes.title IS 'Title of the source code';
COMMENT ON COLUMN source_codes.description IS 'Description of what the code does';
COMMENT ON COLUMN source_codes.content IS 'Actual source code content';
COMMENT ON COLUMN source_codes.file_name IS 'Original file name';
COMMENT ON COLUMN source_codes.file_extension IS 'File extension for language detection';
COMMENT ON COLUMN source_codes.programming_language IS 'Detected or specified programming language';
COMMENT ON COLUMN source_codes.line_count IS 'Number of lines in the source code';
COMMENT ON COLUMN source_codes.character_count IS 'Total character count';
COMMENT ON COLUMN source_codes.size_bytes IS 'Size in bytes of the content';
COMMENT ON COLUMN source_codes.status IS 'Current status (active, archived, etc.)';
COMMENT ON COLUMN source_codes.is_public IS 'Whether the code is publicly visible';
COMMENT ON COLUMN source_codes.is_processed IS 'Whether the code has been processed for analysis';
COMMENT ON COLUMN source_codes.processing_status IS 'Processing status: pending, processing, completed, error';
COMMENT ON COLUMN source_codes.user_id IS 'Reference to auth.users table - who owns this code';
COMMENT ON COLUMN source_codes.created_at IS 'Timestamp when the record was created';
COMMENT ON COLUMN source_codes.updated_at IS 'Timestamp when the record was last updated';

-- =================================================================
-- VERIFICAÇÃO (opcional)
-- Execute estas consultas para verificar se tudo foi criado corretamente
-- =================================================================

-- Verificar se a tabela existe
-- SELECT table_name FROM information_schema.tables
-- WHERE table_schema = 'public' AND table_name = 'source_codes';

-- Verificar estrutura das colunas
-- SELECT column_name, data_type, is_nullable, column_default
-- FROM information_schema.columns
-- WHERE table_schema = 'public' AND table_name = 'source_codes'
-- ORDER BY ordinal_position;

-- Verificar índices
-- SELECT indexname, indexdef FROM pg_indexes
-- WHERE schemaname = 'public' AND tablename = 'source_codes';

-- Verificar se RLS está habilitado
-- SELECT rowsecurity FROM pg_tables
-- WHERE schemaname = 'public' AND tablename = 'source_codes';

-- Verificar políticas RLS
-- SELECT policyname, cmd, roles FROM pg_policies
-- WHERE tablename = 'source_codes';

-- =================================================================
-- TESTE DE INSERÇÃO (opcional)
-- Descomente para testar se a tabela está funcionando
-- =================================================================

-- INSERT INTO source_codes (
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
--     'test_001',
--     'Hello World Test',
--     'Simple hello world program',
--     'console.log("Hello, World!");',
--     'hello.js',
--     'js',
--     'javascript',
--     1,
--     26,
--     26
-- );

-- SELECT * FROM source_codes WHERE code_id = 'test_001';

-- Limpar teste
-- DELETE FROM source_codes WHERE code_id = 'test_001';

-- =================================================================
-- FIM DO SCRIPT
-- =================================================================