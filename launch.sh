#!/bin/bash
set -e

echo "Setting up Supabase with Unfindables..."

cd supabase/docker
docker-compose up -d

cd ../../

echo "Starting Unfindables services..."

docker-compose up -d