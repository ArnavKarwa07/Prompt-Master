-- =====================================================
-- Prompt Master - Migration V2
-- Decouples prompt_history from projects
-- Adds user_id directly to prompt_history
-- =====================================================

-- 1. Add user_id column to prompt_history (allow NULL temporarily for migration)
ALTER TABLE prompt_history 
ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES users(id) ON DELETE CASCADE;

-- 2. Make project_id optional (remove NOT NULL constraint)
ALTER TABLE prompt_history 
ALTER COLUMN project_id DROP NOT NULL;

-- 3. Migrate existing data: populate user_id from projects table
UPDATE prompt_history ph
SET user_id = p.user_id
FROM projects p
WHERE ph.project_id = p.id AND ph.user_id IS NULL;

-- 4. Add index for user-based queries
CREATE INDEX IF NOT EXISTS idx_prompt_history_user_id ON prompt_history(user_id);

-- =====================================================
-- STORAGE BUCKET SETUP
-- Run this in Supabase Dashboard -> Storage -> Create bucket
-- Bucket name: user-files
-- Public: false
-- =====================================================

-- =====================================================
-- USER_CONTEXT_VECTORS TABLE
-- Store embeddings per user/project for RAG
-- =====================================================
CREATE TABLE IF NOT EXISTS user_context_vectors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    embedding vector(1536),
    content_text TEXT,  -- Original text chunk
    file_name VARCHAR(255),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for user context vectors
CREATE INDEX IF NOT EXISTS idx_user_context_vectors_user_id ON user_context_vectors(user_id);
CREATE INDEX IF NOT EXISTS idx_user_context_vectors_project_id ON user_context_vectors(project_id);

-- Vector search index (IVFFlat)
CREATE INDEX IF NOT EXISTS idx_user_context_vectors_embedding 
ON user_context_vectors 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- RLS Policy for user_context_vectors
ALTER TABLE user_context_vectors ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Service role full access on user_context_vectors" ON user_context_vectors
    FOR ALL USING (auth.role() = 'service_role');

-- =====================================================
-- VECTOR SIMILARITY SEARCH FUNCTION FOR USER CONTEXT
-- =====================================================
CREATE OR REPLACE FUNCTION match_user_context_vectors(
    query_embedding vector(1536),
    p_user_id UUID,
    p_project_id UUID DEFAULT NULL,
    match_threshold FLOAT DEFAULT 0.7,
    match_count INT DEFAULT 5
)
RETURNS TABLE (
    id UUID,
    content_text TEXT,
    file_name VARCHAR(255),
    metadata JSONB,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        ucv.id,
        ucv.content_text,
        ucv.file_name,
        ucv.metadata,
        1 - (ucv.embedding <=> query_embedding) AS similarity
    FROM user_context_vectors ucv
    WHERE ucv.user_id = p_user_id
      AND (p_project_id IS NULL OR ucv.project_id = p_project_id)
      AND 1 - (ucv.embedding <=> query_embedding) > match_threshold
    ORDER BY ucv.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- =====================================================
-- USER_ANALYTICS TABLE
-- Store analytics per user (separate from projects)
-- =====================================================
CREATE TABLE IF NOT EXISTS user_analytics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    total_prompts INTEGER DEFAULT 0,
    total_score_sum INTEGER DEFAULT 0,  -- For calculating average
    agent_usage JSONB DEFAULT '{}',  -- {"coding": 5, "creative": 3, ...}
    last_activity TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for user analytics
CREATE INDEX IF NOT EXISTS idx_user_analytics_user_id ON user_analytics(user_id);

-- RLS Policy
ALTER TABLE user_analytics ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Service role full access on user_analytics" ON user_analytics
    FOR ALL USING (auth.role() = 'service_role');
