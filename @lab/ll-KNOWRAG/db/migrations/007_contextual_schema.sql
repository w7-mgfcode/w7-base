-- 007_contextual_schema.sql
-- Add contextual_content column to chunks table

ALTER TABLE kb_chunks
ADD COLUMN IF NOT EXISTS contextual_content TEXT;
