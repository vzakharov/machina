# Supabase Docker Configuration

This directory contains a copy of the Docker configuration files from the official Supabase repository, allowing you to run Supabase locally. Ideally, you don’t want to change _anything_ in this directory, as your changes will be lost when you update the Docker configuration (see **Updating** below).

Instead, you want to run `docker-compose up` from within `supabase/docker` to start Supabase, and then use the created container network from within your project to connect to Supabase. The existing `../docker-compose.yml` in the repo root already supports this, and the `../launch.sh` script will also start Supabase for you.

## What's Included

- `docker/` - Contains Docker Compose files and configuration from the official Supabase repository
- `update.sh` - Script to update the Docker configuration to the latest version
- `README.md` - This file

## Updating

The Docker configuration should ideally be kept up to date with the latest Supabase version. You can update it by running:

```bash
chmod +x update.sh
./update.sh
```

## Important Notes

- The update script uses git sparse-checkout to download only the `docker/` directory from Supabase
- Before updating, be aware that newer Supabase versions may not be backward compatible
- Always check the changes after updating to ensure they still work within our repository's structure and workflows 