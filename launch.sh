#!/bin/bash
set -e

echo "Setting up Supabase with Machina..."

cd supabase/docker
docker-compose up -d

cd ../../

echo "Starting Machina services..."

docker-compose up -d