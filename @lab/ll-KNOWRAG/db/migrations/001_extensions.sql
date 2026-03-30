-- 001_extensions.sql
-- Enable required extensions for KnowRAG

-- Enable pgvector for semantic search
CREATE EXTENSION IF NOT EXISTS vector;

-- Enable pg_trgm for fuzzy text matching and hybrid search
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Enable pgcrypto for UUID generation and encryption
CREATE EXTENSION IF NOT EXISTS pgcrypto;
