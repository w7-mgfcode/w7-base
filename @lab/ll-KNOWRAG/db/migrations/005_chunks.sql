-- 005_chunks.sql
-- Semantic search units with vector embeddings

CREATE TABLE IF NOT EXISTS kb_chunks (
    id BIGSERIAL PRIMARY KEY,
    source_id TEXT NOT NULL REFERENCES kb_sources(source_id) ON DELETE CASCADE,
    page_id UUID REFERENCES kb_pages(id) ON DELETE CASCADE,
    url TEXT NOT NULL,
    chunk_number INTEGER NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    embedding VECTOR(768), -- Default for nomic-embed-text
    embedding_model TEXT,
    embedding_dimension INTEGER DEFAULT 768,
    llm_chat_model TEXT,
    content_search_vector TSVECTOR GENERATED ALWAYS AS (to_tsvector('english', content)) STORED,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(url, chunk_number)
);

-- Vector Similarity Index (HNSW for performance)
CREATE INDEX IF NOT EXISTS idx_kb_chunks_embedding ON kb_chunks USING hnsw (embedding vector_cosine_ops);

-- Full-Text Search Index
CREATE INDEX IF NOT EXISTS idx_kb_chunks_content_search ON kb_chunks USING GIN (content_search_vector);

-- Trigram Index for fuzzy matching
CREATE INDEX IF NOT EXISTS idx_kb_chunks_content_trgm ON kb_chunks USING GIN (content gin_trgm_ops);

-- Metadata Index
CREATE INDEX IF NOT EXISTS idx_kb_chunks_metadata ON kb_chunks USING GIN (metadata);

-- Relational Lookups
CREATE INDEX IF NOT EXISTS idx_kb_chunks_source_id ON kb_chunks(source_id);
CREATE INDEX IF NOT EXISTS idx_kb_chunks_page_id ON kb_chunks(page_id);
