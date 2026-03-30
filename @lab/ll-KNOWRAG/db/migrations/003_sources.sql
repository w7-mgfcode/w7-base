-- 003_sources.sql
-- Root ingestion entities for the Knowledge Base

CREATE TABLE IF NOT EXISTS kb_sources (
    source_id TEXT PRIMARY KEY,
    source_url TEXT,
    source_display_name TEXT,
    title TEXT,
    summary TEXT,
    metadata JSONB DEFAULT '{}',
    total_word_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TRIGGER update_kb_sources_updated_at
    BEFORE UPDATE ON kb_sources
    FOR EACH ROW
    EXECUTE PROCEDURE update_updated_at_column();

CREATE INDEX IF NOT EXISTS idx_kb_sources_metadata ON kb_sources USING GIN (metadata);
