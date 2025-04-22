# Supabase Docker Configuration

This directory contains a copy of the Docker configuration files from the official Supabase repository, allowing you to run Supabase locally.

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