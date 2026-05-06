-- RPC function: return sources with per-source page and chunk counts
CREATE OR REPLACE FUNCTION get_sources_with_counts()
RETURNS TABLE (
    source_id TEXT,
    source_url TEXT,
    source_display_name TEXT,
    title TEXT,
    summary TEXT,
    metadata JSONB,
    total_word_count INTEGER,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ,
    page_count BIGINT,
    chunk_count BIGINT
) AS $$
    SELECT
        s.source_id,
        s.source_url,
        s.source_display_name,
        s.title,
        s.summary,
        s.metadata,
        s.total_word_count,
        s.created_at,
        s.updated_at,
        COALESCE(p.cnt, 0) AS page_count,
        COALESCE(c.cnt, 0) AS chunk_count
    FROM kb_sources s
    LEFT JOIN (
        SELECT source_id, COUNT(*) AS cnt FROM kb_pages GROUP BY source_id
    ) p ON p.source_id = s.source_id
    LEFT JOIN (
        SELECT source_id, COUNT(*) AS cnt FROM kb_chunks GROUP BY source_id
    ) c ON c.source_id = s.source_id
    ORDER BY s.updated_at DESC;
$$ LANGUAGE SQL STABLE;
