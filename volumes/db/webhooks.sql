CREATE SCHEMA IF NOT EXISTS supabase_functions;

CREATE TABLE IF NOT EXISTS supabase_functions.hooks (
  id bigserial PRIMARY KEY,
  hook_table_id uuid REFERENCES supabase_functions.hooks ON DELETE CASCADE,
  hook_name text,
  created_at timestamptz DEFAULT NOW(),
  request_id uuid
);

CREATE OR REPLACE FUNCTION supabase_functions.create_hooks_for_table() 
RETURNS event_trigger 
LANGUAGE plpgsql 
AS $$
DECLARE
  r RECORD;
BEGIN
  FOR r IN SELECT * FROM pg_event_trigger_ddl_commands() WHERE command_tag IN ('CREATE TABLE', 'ALTER TABLE')
  LOOP
    IF position('hooks' in r.object_identity) > 0 THEN
      INSERT INTO supabase_functions.hooks (hook_table_id, hook_name, request_id)
      VALUES (gen_random_uuid(), TG_ARGV[0], gen_random_uuid());
    END IF;
  END LOOP;
END;
$$; 

-- Create a configurable webhook function that can send to different endpoints
-- It uses the webhook_url parameter to determine where to send the webhook
CREATE OR REPLACE FUNCTION public.handle_table_change(webhook_url TEXT, auth_token TEXT DEFAULT NULL)
RETURNS TRIGGER AS $$
DECLARE
  headers JSONB;
BEGIN
  -- Build headers with auth token if provided
  IF auth_token IS NOT NULL THEN
    headers := jsonb_build_object(
      'Content-Type', 'application/json',
      'Authorization', concat('Bearer ', auth_token)
    );
  ELSE
    headers := jsonb_build_object('Content-Type', 'application/json');
  END IF;

  PERFORM net.http_post(
    webhook_url,  -- Configurable endpoint
    jsonb_build_object(
      'table', TG_TABLE_NAME,
      'schema', TG_TABLE_SCHEMA,
      'operation', TG_OP,
      'new_record', CASE WHEN TG_OP = 'DELETE' THEN NULL ELSE row_to_json(NEW) END,
      'old_record', CASE WHEN TG_OP = 'INSERT' THEN NULL ELSE row_to_json(OLD) END
    ),
    headers,
    '10000'
  );
  RETURN NULL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create a function to automatically add triggers to all tables in a schema
CREATE OR REPLACE FUNCTION public.create_webhook_triggers_for_all_tables(
  target_schema TEXT DEFAULT 'public',
  django_url TEXT DEFAULT NULL,
  nextjs_url TEXT DEFAULT NULL,
  django_auth_token TEXT DEFAULT NULL,
  nextjs_auth_token TEXT DEFAULT NULL
)
RETURNS VOID AS $$
DECLARE
  table_record RECORD;
  trigger_name TEXT;
BEGIN
  -- Loop through all tables in the specified schema
  FOR table_record IN 
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = target_schema
    AND table_type = 'BASE TABLE'
  LOOP
    -- Create Django webhook trigger if URL is provided
    IF django_url IS NOT NULL THEN
      trigger_name := table_record.table_name || '_django_webhook';
      EXECUTE format('
        DROP TRIGGER IF EXISTS %I ON %I.%I;
        CREATE TRIGGER %I
        AFTER INSERT OR UPDATE OR DELETE ON %I.%I
        FOR EACH ROW 
        EXECUTE FUNCTION public.handle_table_change(%L, %L);
      ', 
      trigger_name, target_schema, table_record.table_name,
      trigger_name, target_schema, table_record.table_name,
      django_url, django_auth_token);
    END IF;
    
    -- Create Next.js webhook trigger if URL is provided
    IF nextjs_url IS NOT NULL THEN
      trigger_name := table_record.table_name || '_nextjs_webhook';
      EXECUTE format('
        DROP TRIGGER IF EXISTS %I ON %I.%I;
        CREATE TRIGGER %I
        AFTER INSERT OR UPDATE OR DELETE ON %I.%I
        FOR EACH ROW 
        EXECUTE FUNCTION public.handle_table_change(%L, %L);
      ', 
      trigger_name, target_schema, table_record.table_name,
      trigger_name, target_schema, table_record.table_name,
      nextjs_url, nextjs_auth_token);
    END IF;
  END LOOP;
END;
$$ LANGUAGE plpgsql;

-- Create function to get environment variables with defaults
CREATE OR REPLACE FUNCTION public.get_env_var(var_name TEXT, default_value TEXT DEFAULT NULL)
RETURNS TEXT AS $$
DECLARE
  env_value TEXT;
BEGIN
  -- Try to get from PostgreSQL environment variables
  BEGIN
    EXECUTE format('SELECT current_setting(''app.settings.%s'')', var_name) INTO env_value;
    IF env_value IS NOT NULL AND env_value != '' THEN
      RETURN env_value;
    END IF;
  EXCEPTION WHEN OTHERS THEN
    -- If setting doesn't exist, use default
    RETURN default_value;
  END;
  
  RETURN default_value;
END;
$$ LANGUAGE plpgsql;

-- This commented section shows how to use the functions above

-- To set up environment-specific webhook URLs
-- EXECUTE 'ALTER DATABASE postgres SET app.settings.webhook_url_django TO ''https://production-django.example.com/api/webhooks/supabase''';
-- EXECUTE 'ALTER DATABASE postgres SET app.settings.webhook_url_nextjs TO ''https://production-nextjs.example.com/api/webhooks/supabase''';

-- To create triggers for all tables in the public schema:
-- SELECT public.create_webhook_triggers_for_all_tables(
--   'public',
--   public.get_env_var('django_url'),
--   public.get_env_var('nextjs_url'),
--   public.get_env_var('django_auth_token'),
--   public.get_env_var('nextjs_auth_token')
-- );

-- To create a trigger for a specific table manually:
-- CREATE TRIGGER my_table_webhook
-- AFTER INSERT OR UPDATE OR DELETE ON public.my_table
-- FOR EACH ROW EXECUTE FUNCTION public.handle_table_change(public.get_env_var('django_url'), public.get_env_var('django_auth_token')); 