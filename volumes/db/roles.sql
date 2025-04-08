-- Create authenticator role
CREATE ROLE authenticator NOINHERIT LOGIN PASSWORD '${POSTGRES_PASSWORD}';

-- Create anon role
CREATE ROLE anon;
GRANT anon TO authenticator;

-- Create authenticated role
CREATE ROLE authenticated;
GRANT authenticated TO authenticator;

-- Create supabase_auth_admin role
CREATE ROLE supabase_auth_admin NOINHERIT CREATEROLE LOGIN PASSWORD '${POSTGRES_PASSWORD}';

-- Create supabase_storage_admin role
CREATE ROLE supabase_storage_admin NOINHERIT CREATEROLE LOGIN PASSWORD '${POSTGRES_PASSWORD}';

-- Create supabase_admin role
CREATE ROLE supabase_admin NOINHERIT CREATEROLE LOGIN PASSWORD '${POSTGRES_PASSWORD}';

-- Grant privileges
GRANT CREATE ON DATABASE postgres TO supabase_admin;
ALTER USER postgres SET search_path TO public; 