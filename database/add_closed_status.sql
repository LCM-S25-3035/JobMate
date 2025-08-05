-- SQL Script to Add 'closed' Status to job_postings Table (PostgreSQL)
-- Run this script to add support for 'closed' status in job postings

-- Add 'closed' to the job_status ENUM type
ALTER TYPE job_status ADD VALUE 'closed';

-- Verify the change
SELECT enumlabel FROM pg_enum WHERE enumtypid = (
    SELECT oid FROM pg_type WHERE typname = 'job_status'
) ORDER BY enumsortorder;

-- Optional: Add index on status column for better performance (if not exists)
-- CREATE INDEX IF NOT EXISTS idx_job_postings_status ON job_postings(status);
