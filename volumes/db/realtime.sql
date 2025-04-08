-- Setup Realtime
CREATE SCHEMA IF NOT EXISTS realtime;

-- Realtime tables
CREATE TABLE IF NOT EXISTS realtime.subscription (
    id bigint PRIMARY KEY,
    subscription_id uuid NOT NULL,
    entity regclass NOT NULL,
    filters jsonb NOT NULL,
    claims jsonb NOT NULL,
    created_at timestamp NOT NULL
);

CREATE TABLE IF NOT EXISTS realtime.tenant (
    id uuid PRIMARY KEY,
    name text NOT NULL,
    external_id text,
    max_realtime_connections integer,
    max_realtime_subscriptions integer,
    max_channels integer
);

-- Setup extension
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Realtime RLS
ALTER TABLE realtime.subscription ENABLE ROW LEVEL SECURITY;
ALTER TABLE realtime.tenant ENABLE ROW LEVEL SECURITY; 