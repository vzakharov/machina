-- Create roles required by Supabase
CREATE ROLE anon NOLOGIN;
CREATE ROLE authenticated NOLOGIN;
CREATE ROLE service_role NOLOGIN;
CREATE ROLE supabase_admin NOINHERIT CREATEROLE LOGIN PASSWORD 'postgres';
CREATE ROLE authenticator NOINHERIT LOGIN PASSWORD 'postgres';
CREATE ROLE supabase_storage_admin NOINHERIT CREATEROLE LOGIN PASSWORD 'postgres';

-- Grant permissions
GRANT anon TO authenticator;
GRANT authenticated TO authenticator;
GRANT service_role TO authenticator;
GRANT supabase_admin TO postgres;

-- Setup schemas
CREATE SCHEMA IF NOT EXISTS auth AUTHORIZATION supabase_admin;
CREATE SCHEMA IF NOT EXISTS storage AUTHORIZATION supabase_storage_admin;
CREATE SCHEMA IF NOT EXISTS graphql_public;
CREATE SCHEMA IF NOT EXISTS realtime;

-- Set search path
ALTER ROLE postgres SET search_path TO public;
ALTER ROLE anon SET search_path TO public;
ALTER ROLE authenticated SET search_path TO public;
ALTER ROLE service_role SET search_path TO public;

-- Extension for UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create basic tables for auth schema
CREATE TABLE IF NOT EXISTS auth.users (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  email TEXT UNIQUE,
  encrypted_password TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW())
);

-- Create storage bucket table
CREATE TABLE IF NOT EXISTS storage.buckets (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW())
);

-- Create storage objects table
CREATE TABLE IF NOT EXISTS storage.objects (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  bucket_id TEXT REFERENCES storage.buckets(id),
  name TEXT NOT NULL,
  size INTEGER,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()),
  UNIQUE (bucket_id, name)
);

-- Create default public bucket
INSERT INTO storage.buckets (id, name)
VALUES ('public', 'Public') 
ON CONFLICT DO NOTHING; 