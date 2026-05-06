-- 004_pages.sql
-- Full document content storage

CREATE TABLE IF NOT EXISTS kb_pages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id TEXT NOT NULL REFERENCES kb_sources(source_id) ON DELETE CASCADE,
    url TEXT UNIQUE NOT NULL,
    full_content TEXT NOT NULL,
    section_title TEXT,
    section_order INTEGER DEFAULT 0,
    word_count INTEGER NOT NULL DEFAULT 0,
    char_count INTEGER NOT NULL DEFAULT 0,
    chunk_count INTEGER DEFAULT 0,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TRIGGER update_kb_pages_updated_at
    BEFORE UPDATE ON kb_pages
    FOR EACH ROW
    EXECUTE PROCEDURE update_updated_at_column();

CREATE INDEX IF NOT EXISTS idx_kb_pages_source_id ON kb_pages(source_id);
CREATE INDEX IF NOT EXISTS idx_kb_pages_metadata ON kb_pages USING GIN (metadata);
