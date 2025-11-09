#!/bin/bash
set -e

echo "🎭 Starting MuseTalk Real API in DEVELOPMENT mode..."

# Load environment variables from .env file  
if [ -f /app/.env ]; then
    echo "🔧 Loading environment variables..."
    export $(cat /app/.env | grep -v '^#' | xargs)
fi

echo "🚀 Starting real API server with debug mode..."
exec python api/main.py --debug --reload