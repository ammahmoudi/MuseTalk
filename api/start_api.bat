@echo off
REM 🚀 MuseTalk Legendary API Startup Script (Windows)

echo 🚀 Starting MuseTalk Legendary API...

REM Check if models exist
if not exist "models" (
    echo 📦 Models not found! Running download script...
    if exist "download_weights.bat" (
        call download_weights.bat
    ) else (
        echo ❌ Download script not found!
        exit /b 1
    )
)

REM Create necessary directories
mkdir temp >nul 2>&1
mkdir results >nul 2>&1
mkdir api\temp >nul 2>&1

echo 🔧 Starting with UV (fast!)...
cd api

echo ⚡ Starting the legendary API server...
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload

echo 🎉 MuseTalk Legendary API is running on http://localhost:8000
echo 📚 API docs available at http://localhost:8000/docs
pause