#!/bin/bash
set -e

echo "Setting up Supabase with Unfindables..."

cd supabase/docker
docker-compose up -d

while true; do
    docker-compose exec supabase status
    if [ $? -eq 0 ]; then
        break
    fi
    sleep 5
done

cd ../../

echo "Starting Unfindables services..."

docker-compose up