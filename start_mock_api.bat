@echo off
echo 🎭 Starting MuseTalk Mock API Server...
echo.
echo This mock API provides instant responses for testing without GPU processing!
echo.
echo Mock API Features:
echo - Instant avatar preparation (2 seconds)
echo - Instant video generation (3-4 seconds)  
echo - Uses test data from test_assets/ folder
echo - Same endpoints as real API
echo.
echo Mock API will be available at: http://localhost:8001
echo Real API runs on: http://localhost:8000
echo.
echo Press Ctrl+C to stop the server
echo ================================
echo.

cd /d "%~dp0"
python api/mock_api.py