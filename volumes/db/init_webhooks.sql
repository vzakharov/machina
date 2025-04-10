-- This file will be executed during initialization to set up all webhooks

-- First, ensure the 'net' extension is enabled
CREATE EXTENSION IF NOT EXISTS "pg_net";

-- Load environment variables into PostgreSQL settings
-- This allows us to access environment variables via SQL
DO $$
BEGIN
  -- Default URLs for local development using service names
  EXECUTE format('ALTER DATABASE postgres SET app.settings.webhook_url_django TO %L', 
    COALESCE(current_setting('webhook_url_django', true), 'http://django:8000/api/webhooks/supabase'));
  
  EXECUTE format('ALTER DATABASE postgres SET app.settings.webhook_url_nextjs TO %L', 
    COALESCE(current_setting('webhook_url_nextjs', true), 'http://nextjs:3000/api/webhooks/supabase'));
  
  -- Auth tokens (empty by default for local dev)
  EXECUTE format('ALTER DATABASE postgres SET app.settings.webhook_auth_django TO %L', 
    COALESCE(current_setting('webhook_auth_django', true), ''));
  
  EXECUTE format('ALTER DATABASE postgres SET app.settings.webhook_auth_nextjs TO %L', 
    COALESCE(current_setting('webhook_auth_nextjs', true), ''));
  
  -- Output settings for debugging
  RAISE NOTICE 'Django webhook URL: %', current_setting('app.settings.webhook_url_django');
  RAISE NOTICE 'Next.js webhook URL: %', current_setting('app.settings.webhook_url_nextjs');
END $$;

-- Create triggers for all existing tables in the public schema
-- This will automatically create webhook triggers for all tables
DO $$
BEGIN
  -- Wait a bit for any other init scripts to complete
  PERFORM pg_sleep(3);
  
  -- Get URLs and auth tokens from settings
  PERFORM public.create_webhook_triggers_for_all_tables(
    'public',
    public.get_env_var('webhook_url_django', 'http://django:8000/api/webhooks/supabase'),
    public.get_env_var('webhook_url_nextjs', 'http://nextjs:3000/api/webhooks/supabase'),
    public.get_env_var('webhook_auth_django', NULL),
    public.get_env_var('webhook_auth_nextjs', NULL)
  );
END $$;

-- Create an event trigger that will add webhooks to any newly created tables
CREATE OR REPLACE FUNCTION public.add_webhooks_to_new_table()
RETURNS event_trigger 
LANGUAGE plpgsql 
AS $$
DECLARE
  r RECORD;
  table_schema TEXT;
  table_name TEXT;
  django_url TEXT;
  nextjs_url TEXT;
  django_auth TEXT;
  nextjs_auth TEXT;
BEGIN
  -- Get the webhook URLs and auth tokens from settings
  django_url := public.get_env_var('webhook_url_django', 'http://django:8000/api/webhooks/supabase');
  nextjs_url := public.get_env_var('webhook_url_nextjs', 'http://nextjs:3000/api/webhooks/supabase');
  django_auth := public.get_env_var('webhook_auth_django', NULL);
  nextjs_auth := public.get_env_var('webhook_auth_nextjs', NULL);
  
  FOR r IN SELECT * FROM pg_event_trigger_ddl_commands() WHERE command_tag = 'CREATE TABLE'
  LOOP
    -- Extract schema and table name
    table_schema := split_part(r.object_identity, '.', 1);
    table_name := split_part(r.object_identity, '.', 2);
    
    -- Skip if not in public schema
    IF table_schema = 'public' THEN
      -- Create Django webhook
      EXECUTE format('
        CREATE TRIGGER %I
        AFTER INSERT OR UPDATE OR DELETE ON %s
        FOR EACH ROW 
        EXECUTE FUNCTION public.handle_table_change(%L, %L);
      ', 
      table_name || '_django_webhook', 
      r.object_identity,
      django_url, django_auth);
      
      -- Create Next.js webhook
      EXECUTE format('
        CREATE TRIGGER %I
        AFTER INSERT OR UPDATE OR DELETE ON %s
        FOR EACH ROW 
        EXECUTE FUNCTION public.handle_table_change(%L, %L);
      ', 
      table_name || '_nextjs_webhook', 
      r.object_identity,
      nextjs_url, nextjs_auth);
    END IF;
  END LOOP;
END;
$$;

-- Create the event trigger to automatically add webhooks to new tables
DROP EVENT TRIGGER IF EXISTS table_webhook_trigger;
CREATE EVENT TRIGGER table_webhook_trigger 
ON ddl_command_end
WHEN tag IN ('CREATE TABLE')
EXECUTE FUNCTION public.add_webhooks_to_new_table(); 