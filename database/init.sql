-- JobMate PostgreSQL Initialization Script
-- This script sets up the database with necessary extensions and initial configurations

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "unaccent";

-- Set timezone
SET timezone = 'UTC';

-- Create indexes for better performance (will be created by Flask-Migrate)
-- These are just examples of what could be added

-- Grant comprehensive privileges to jobmate_user
GRANT ALL PRIVILEGES ON DATABASE jobmate_db TO jobmate_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO jobmate_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO jobmate_user;
GRANT ALL PRIVILEGES ON SCHEMA public TO jobmate_user;

-- Grant future privileges on tables and sequences
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO jobmate_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO jobmate_user;

-- Create a function to check if bio column exists and add it if necessary
CREATE OR REPLACE FUNCTION add_bio_fields_if_not_exists()
RETURNS TEXT AS $$
DECLARE
    result TEXT := '';
BEGIN
    -- Check and add bio column
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'users' AND column_name = 'bio'
    ) THEN
        ALTER TABLE users ADD COLUMN bio TEXT;
        result := result || 'Added bio column. ';
    END IF;
    
    -- Check and add skills column
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'users' AND column_name = 'skills'
    ) THEN
        ALTER TABLE users ADD COLUMN skills VARCHAR(500);
        result := result || 'Added skills column. ';
    END IF;
    
    -- Check and add experience_level column
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'users' AND column_name = 'experience_level'
    ) THEN
        ALTER TABLE users ADD COLUMN experience_level VARCHAR(50);
        result := result || 'Added experience_level column. ';
    END IF;
    
    IF result = '' THEN
        result := 'All bio-related columns already exist.';
    END IF;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- Default configurations for better performance
ALTER SYSTEM SET shared_preload_libraries = 'pg_stat_statements';
ALTER SYSTEM SET max_connections = 200;
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET work_mem = '4MB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';

-- Restart required for some settings to take effect
SELECT pg_reload_conf();

-- Create a simple health check function
CREATE OR REPLACE FUNCTION public.health_check()
RETURNS JSON AS $$
BEGIN
    RETURN json_build_object(
        'status', 'healthy',
        'timestamp', NOW(),
        'version', version(),
        'uptime', EXTRACT(EPOCH FROM (NOW() - pg_postmaster_start_time()))
    );
END;
$$ LANGUAGE plpgsql; 