#!/bin/bash
set -e

echo "🎭 Starting MuseTalk Mock API in PRODUCTION mode..."

# Load environment variables from .env file
if [ -f /app/.env ]; then
    echo "🔧 Loading environment variables..."
    export $(cat /app/.env | grep -v '^#' | xargs)
fi

echo "🎯 Starting production mock API server..."
exec python mock_api.py