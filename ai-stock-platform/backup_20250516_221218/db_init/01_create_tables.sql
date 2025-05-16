-- This script creates any tables that might not be included in Alembic migrations
-- Typically used for supplementary tables like reference data

-- Market sectors reference table (if not already in migrations)
CREATE TABLE IF NOT EXISTS market_sectors (
    id SERIAL PRIMARY KEY,
    code VARCHAR(10) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    description TEXT
);

-- System configuration table for storing app configuration
CREATE TABLE IF NOT EXISTS system_config (
    key VARCHAR(100) NOT NULL PRIMARY KEY,
    value JSONB NOT NULL,
    description TEXT,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_by VARCHAR(100)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_system_config_key ON system_config (key);