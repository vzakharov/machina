#!/bin/bash
set -e

echo "Stopping Machina services..."

docker-compose down

echo "Stopping Supabase services..."
cd supabase/docker
docker-compose down
