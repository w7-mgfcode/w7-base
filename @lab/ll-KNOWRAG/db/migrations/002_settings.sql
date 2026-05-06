-- 002_settings.sql
-- Global and provider settings for the KB system

CREATE TABLE IF NOT EXISTS kb_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key TEXT UNIQUE NOT NULL,
    value TEXT,
    encrypted_value TEXT,
    is_encrypted BOOLEAN DEFAULT FALSE,
    category TEXT,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Trigger to update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_kb_settings_updated_at
    BEFORE UPDATE ON kb_settings
    FOR EACH ROW
    EXECUTE PROCEDURE update_updated_at_column();
