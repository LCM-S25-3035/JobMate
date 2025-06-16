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

-- Grant privileges to jobmate_user
GRANT ALL PRIVILEGES ON DATABASE jobmate_db TO jobmate_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO jobmate_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO jobmate_user;

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