-- Install pg_net extension and set permissions directly
CREATE SCHEMA IF NOT EXISTS extensions;
ALTER DATABASE postgres SET search_path TO "$user", public, extensions;

-- Create necessary roles
DO $$ 
BEGIN
    -- Create the standard Supabase roles if they don't exist
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'supabase_admin') THEN
        CREATE ROLE supabase_admin NOINHERIT CREATEROLE LOGIN PASSWORD 'postgres';
    END IF;
    
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'anon') THEN
        CREATE ROLE anon NOLOGIN NOINHERIT;
    END IF;
    
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'authenticated') THEN
        CREATE ROLE authenticated NOLOGIN NOINHERIT;
    END IF;
    
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'service_role') THEN
        CREATE ROLE service_role NOLOGIN NOINHERIT;
    END IF;
    
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'supabase_functions_admin') THEN
        CREATE ROLE supabase_functions_admin NOINHERIT CREATEROLE LOGIN NOREPLICATION;
    END IF;
END $$;

-- This is needed for pg_net to have proper access to system functions
ALTER USER postgres WITH SUPERUSER;

-- Create the pg_net extension
CREATE EXTENSION IF NOT EXISTS pg_net SCHEMA extensions;

-- Set up permissions for the extension
GRANT USAGE ON SCHEMA extensions TO postgres, anon, authenticated, service_role, supabase_functions_admin;
GRANT ALL ON SCHEMA extensions TO postgres;

-- When used with handle_table_change, we need these permissions
CREATE SCHEMA IF NOT EXISTS net;
GRANT USAGE ON SCHEMA net TO postgres, anon, authenticated, service_role, supabase_functions_admin;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA net TO postgres, anon, authenticated, service_role, supabase_functions_admin;

-- Make webhooks run in a secure context
ALTER FUNCTION net.http_get(url text, params jsonb, headers jsonb, timeout_milliseconds integer) SECURITY DEFINER;
ALTER FUNCTION net.http_post(url text, body jsonb, params jsonb, headers jsonb, timeout_milliseconds integer) SECURITY DEFINER;

-- Set search path for security
ALTER FUNCTION net.http_get(url text, params jsonb, headers jsonb, timeout_milliseconds integer) SET search_path = net;
ALTER FUNCTION net.http_post(url text, body jsonb, params jsonb, headers jsonb, timeout_milliseconds integer) SET search_path = net; 