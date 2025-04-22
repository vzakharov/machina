#!/bin/bash

set -e

TEMP_DIR=$(mktemp -d)
SUPABASE_REPO="https://github.com/supabase/supabase.git"

echo "Created temporary directory: $TEMP_DIR"
echo "Downloading only the docker directory from Supabase..."
git clone --depth=1 --filter=blob:none --sparse $SUPABASE_REPO $TEMP_DIR
ORIGINAL_DIR=$(pwd)
cd $TEMP_DIR
git sparse-checkout set docker

echo "Copying docker directory to script location..."
cd $ORIGINAL_DIR
rm -rf ./docker
cp -r $TEMP_DIR/docker ./docker

echo "Cleaning up temporary directory..."
rm -rf $TEMP_DIR

echo "Done! Supabase docker directory has been updated." 