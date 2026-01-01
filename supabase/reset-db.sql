-- =====================================================
-- Prompt Master - Database Reset Script
-- Run this to completely reset and recreate the database
-- =====================================================

-- Drop existing tables (in correct order due to foreign keys)
DROP TABLE IF EXISTS project_context CASCADE;
DROP TABLE IF EXISTS prompt_history CASCADE;
DROP TABLE IF EXISTS projects CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS knowledge_vectors CASCADE;

-- Drop existing functions
DROP FUNCTION IF EXISTS match_knowledge_vectors CASCADE;
DROP FUNCTION IF EXISTS get_db_size_mb CASCADE;
DROP FUNCTION IF EXISTS cleanup_old_prompt_history CASCADE;
DROP FUNCTION IF EXISTS update_updated_at CASCADE;

-- =====================================================
-- Now run the main schema
-- =====================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

-- =====================================================
-- USERS TABLE
-- Minimal user storage - Clerk handles auth
-- =====================================================
CREATE TABLE users (
    id UUID PRIMARY KEY,  -- Mapped from Clerk user ID via UUID v5
    email VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);

-- =====================================================
-- PROJECTS TABLE
-- Lightweight workspaces for organizing prompts
-- =====================================================
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_projects_user_id ON projects(user_id);

-- =====================================================
-- PROMPT_HISTORY TABLE
-- Store prompt evaluations with minimal text
-- =====================================================
CREATE TABLE prompt_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    prompt_text VARCHAR(1000) NOT NULL,
    optimized_prompt VARCHAR(2000),
    agent_used VARCHAR(50) NOT NULL,
    score INTEGER CHECK (score >= 0 AND score <= 100),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_prompt_history_project_id ON prompt_history(project_id);
CREATE INDEX idx_prompt_history_created_at ON prompt_history(created_at DESC);

-- =====================================================
-- KNOWLEDGE_VECTORS TABLE
-- Shared RAG knowledge base
-- =====================================================
CREATE TABLE knowledge_vectors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    embedding vector(1536),
    chunk_summary VARCHAR(255) NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Vector similarity search index
CREATE INDEX idx_knowledge_vectors_embedding 
ON knowledge_vectors 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- =====================================================
-- PROJECT_CONTEXT TABLE
-- References to files in Supabase Storage
-- =====================================================
CREATE TABLE project_context (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    storage_path VARCHAR(500) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_type VARCHAR(50),
    file_size_bytes INTEGER,
    processed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_project_context_project_id ON project_context(project_id);

-- =====================================================
-- VECTOR SIMILARITY SEARCH FUNCTION
-- =====================================================
CREATE OR REPLACE FUNCTION match_knowledge_vectors(
    query_embedding vector(1536),
    match_threshold FLOAT DEFAULT 0.7,
    match_count INT DEFAULT 5
)
RETURNS TABLE (
    id UUID,
    chunk_summary VARCHAR(255),
    metadata JSONB,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        kv.id,
        kv.chunk_summary,
        kv.metadata,
        1 - (kv.embedding <=> query_embedding) AS similarity
    FROM knowledge_vectors kv
    WHERE 1 - (kv.embedding <=> query_embedding) > match_threshold
    ORDER BY kv.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- =====================================================
-- UTILITY FUNCTIONS
-- =====================================================
CREATE OR REPLACE FUNCTION get_db_size_mb()
RETURNS NUMERIC
LANGUAGE sql
AS $$
    SELECT pg_database_size(current_database()) / (1024 * 1024)::NUMERIC;
$$;

CREATE OR REPLACE FUNCTION cleanup_old_prompt_history()
RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    WITH ranked_history AS (
        SELECT id, ROW_NUMBER() OVER (
            PARTITION BY project_id 
            ORDER BY created_at DESC
        ) as rn
        FROM prompt_history
    )
    DELETE FROM prompt_history
    WHERE id IN (
        SELECT id FROM ranked_history WHERE rn > 50
    );
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$;

CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_projects_updated_at
    BEFORE UPDATE ON projects
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- =====================================================
-- ROW LEVEL SECURITY (RLS)
-- =====================================================
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE prompt_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE project_context ENABLE ROW LEVEL SECURITY;
ALTER TABLE knowledge_vectors ENABLE ROW LEVEL SECURITY;

-- =====================================================
-- SERVICE ROLE BYPASS POLICIES
-- Backend (using service_role key) gets full access
-- =====================================================
CREATE POLICY "Service role full access on users" ON users
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access on projects" ON projects
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access on prompt_history" ON prompt_history
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access on project_context" ON project_context
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access on knowledge_vectors" ON knowledge_vectors
    FOR ALL USING (auth.role() = 'service_role');

-- =====================================================
-- USER-FACING RLS POLICIES (for direct client access)
-- =====================================================
CREATE POLICY "Users can view own profile" ON users
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON users
    FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can view own projects" ON projects
    FOR SELECT USING (user_id = auth.uid());

CREATE POLICY "Users can create own projects" ON projects
    FOR INSERT WITH CHECK (user_id = auth.uid());

CREATE POLICY "Users can update own projects" ON projects
    FOR UPDATE USING (user_id = auth.uid());

CREATE POLICY "Users can delete own projects" ON projects
    FOR DELETE USING (user_id = auth.uid());

CREATE POLICY "Users can view own prompt history" ON prompt_history
    FOR SELECT USING (
        project_id IN (SELECT id FROM projects WHERE user_id = auth.uid())
    );

CREATE POLICY "Users can create prompt history" ON prompt_history
    FOR INSERT WITH CHECK (
        project_id IN (SELECT id FROM projects WHERE user_id = auth.uid())
    );

CREATE POLICY "Users can view own project context" ON project_context
    FOR SELECT USING (
        project_id IN (SELECT id FROM projects WHERE user_id = auth.uid())
    );

CREATE POLICY "Users can create project context" ON project_context
    FOR INSERT WITH CHECK (
        project_id IN (SELECT id FROM projects WHERE user_id = auth.uid())
    );

CREATE POLICY "Authenticated users can read knowledge" ON knowledge_vectors
    FOR SELECT USING (auth.role() = 'authenticated');

-- =====================================================
-- DONE! Database is ready.
-- =====================================================
SELECT 'Database reset complete! Tables created:' as status;
SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
