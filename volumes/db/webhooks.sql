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