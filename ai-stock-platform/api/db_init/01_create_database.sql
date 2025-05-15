-- Initial database creation script
-- This should be run by a user with sufficient privileges

-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS quantumvestai
    WITH 
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8'
    TEMPLATE = template0;

-- Create application user if it doesn't exist
DO
$$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'quantumvest') THEN
        CREATE USER quantumvest WITH ENCRYPTED PASSWORD 'replace_with_secure_password';
    END IF;
END
$$;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE quantumvestai TO quantumvest;

-- Connect to the database to configure it
\c quantumvestai

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Set search path
ALTER ROLE quantumvest SET search_path TO public;

-- Set timezone
ALTER DATABASE quantumvestai SET timezone TO 'UTC';