#!/bin/bash
# 🚀 MuseTalk Legendary API Startup Script

echo "🚀 Starting MuseTalk Legendary API..."

# Check if models exist
if [ ! -d "models" ]; then
    echo "📦 Models not found! Running download script..."
    if [ -f "download_weights.bat" ]; then
        ./download_weights.bat
    elif [ -f "download_weights.sh" ]; then
        ./download_weights.sh
    else
        echo "❌ Download script not found!"
        exit 1
    fi
fi

# Create necessary directories
mkdir -p temp results api/temp

echo "🔧 Installing API dependencies..."
cd api
pip install -r requirements.txt

echo "⚡ Starting the legendary API server..."
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

echo "🎉 MuseTalk Legendary API is running on http://localhost:8000"
echo "📚 API docs available at http://localhost:8000/docs"