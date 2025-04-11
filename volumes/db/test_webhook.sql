-- Function to manually test webhooks
CREATE OR REPLACE FUNCTION public.test_webhooks() RETURNS void AS $$
DECLARE
  django_url TEXT;
  nextjs_url TEXT;
BEGIN
  -- Get URLs from settings
  django_url := public.get_env_var('webhook_url_django', 'http://django:8000/api/webhooks/supabase');
  nextjs_url := public.get_env_var('webhook_url_nextjs', 'http://nextjs:3000/api/webhooks/supabase');
  
  -- Log the URLs
  RAISE NOTICE 'Sending test webhook to Django: %', django_url;
  RAISE NOTICE 'Sending test webhook to Next.js: %', nextjs_url;
  
  -- Send test webhook to Django
  PERFORM net.http_post(
    django_url,
    jsonb_build_object(
      'table', 'test_table',
      'schema', 'public',
      'operation', 'TEST',
      'new_record', jsonb_build_object('id', 1, 'name', 'Test Record'),
      'old_record', NULL
    ),
    '{}'::jsonb,
    jsonb_build_object('Content-Type', 'application/json'),
    10000
  );
  
  -- Send test webhook to Next.js
  PERFORM net.http_post(
    nextjs_url,
    jsonb_build_object(
      'table', 'test_table',
      'schema', 'public',
      'operation', 'TEST',
      'new_record', jsonb_build_object('id', 1, 'name', 'Test Record'),
      'old_record', NULL
    ),
    '{}'::jsonb,
    jsonb_build_object('Content-Type', 'application/json'),
    10000
  );
  
  RAISE NOTICE 'Test webhooks sent!';
END;
$$ LANGUAGE plpgsql;

-- Example usage:
-- SELECT public.test_webhooks(); 