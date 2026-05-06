-- 006_search_functions.sql
-- Database RPC functions for RAG retrieval

-- Vector Search Function
CREATE OR REPLACE FUNCTION match_kb_chunks(
    query_embedding VECTOR(768),
    match_threshold FLOAT,
    match_count INTEGER,
    filter_source_id TEXT DEFAULT NULL
)
RETURNS TABLE (
    id BIGINT,
    source_id TEXT,
    page_id UUID,
    content TEXT,
    metadata JSONB,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        c.id,
        c.source_id,
        c.page_id,
        c.content,
        c.metadata,
        1 - (c.embedding <=> query_embedding) AS similarity
    FROM kb_chunks c
    WHERE (filter_source_id IS NULL OR c.source_id = filter_source_id)
      AND 1 - (c.embedding <=> query_embedding) > match_threshold
    ORDER BY c.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Page Context Retrieval
CREATE OR REPLACE FUNCTION get_page_context(
    target_page_id UUID
)
RETURNS TABLE (
    chunk_number INTEGER,
    content TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        c.chunk_number,
        c.content
    FROM kb_chunks c
    WHERE c.page_id = target_page_id
    ORDER BY c.chunk_number ASC;
END;
$$;

-- Hybrid Search (Placeholder implementation using RRF logic or simple weighted sum)
CREATE OR REPLACE FUNCTION hybrid_search_kb_chunks(
    query_text TEXT,
    query_embedding VECTOR(768),
    match_threshold FLOAT,
    match_count INTEGER,
    full_text_weight FLOAT DEFAULT 1.0,
    vector_weight FLOAT DEFAULT 1.0
)
RETURNS TABLE (
    id BIGINT,
    content TEXT,
    metadata JSONB,
    combined_score FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    WITH vector_matches AS (
        SELECT 
            c.id, 
            1 - (c.embedding <=> query_embedding) as score
        FROM kb_chunks c
        WHERE 1 - (c.embedding <=> query_embedding) > match_threshold
    ),
    text_matches AS (
        SELECT 
            c.id, 
            ts_rank_cd(c.content_search_vector, websearch_to_tsquery('english', query_text)) as score
        FROM kb_chunks c
        WHERE c.content_search_vector @@ websearch_to_tsquery('english', query_text)
    )
    SELECT
        c.id,
        c.content,
        c.metadata,
        (COALESCE(v.score, 0) * vector_weight + COALESCE(t.score, 0) * full_text_weight) as combined_score
    FROM kb_chunks c
    LEFT JOIN vector_matches v ON c.id = v.id
    LEFT JOIN text_matches t ON c.id = t.id
    WHERE v.id IS NOT NULL OR t.id IS NOT NULL
    ORDER BY combined_score DESC
    LIMIT match_count;
END;
$$;
