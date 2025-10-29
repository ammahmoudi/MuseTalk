#!/bin/bash
set -e

echo "🎭 Starting MuseTalk Real API in PRODUCTION mode..."

# Load environment variables from .env file  
if [ -f /app/.env ]; then
    echo "🔧 Loading environment variables..."
    export $(cat /app/.env | grep -v '^#' | xargs)
fi

echo "🎯 Starting production real API server..."
exec python api/main.py