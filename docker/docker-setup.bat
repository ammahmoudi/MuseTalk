@echo off
REM 🚀 MuseTalk Docker Quick Setup Script for Windows

echo 🚀 MuseTalk Docker Setup
echo =======================

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not installed. Please install Docker Desktop first.
    pause
    exit /b 1
)

REM Check if Docker Compose is installed  
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose is not installed. Please install Docker Compose first.
    pause
    exit /b 1
)

REM Create .env file if it doesn't exist
if not exist .env (
    echo 📝 Creating .env file from template...
    copy .env.example .env >nul
    echo ✅ Created .env file. You can edit it to customize settings.
) else (
    echo ✅ .env file already exists.
)

REM Parse command line arguments
if "%1"=="" goto help
if "%1"=="help" goto help
if "%1"=="dev" goto dev
if "%1"=="prod" goto prod  
if "%1"=="mock" goto mock
if "%1"=="full" goto full
if "%1"=="stop" goto stop
if "%1"=="clean" goto clean
if "%1"=="logs" goto logs
goto help

:dev
echo 🔧 Starting development environment (Mock API)...
set COMPOSE_PROFILES=dev,mock,cache
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
echo.
echo ✅ Development environment started!
echo 🌐 Mock API: http://localhost:8001  
echo 🔍 Redis: localhost:6379
goto end

:prod
echo 🚀 Starting production environment (Real API with GPU)...
if not exist "models\musetalk" (
    echo ⚠️  Warning: MuseTalk models not found in .\models\
    echo    Please download models first or the API will not work.
    echo    Run: download_weights.bat
)
set COMPOSE_PROFILES=production,gpu,cache,files
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
echo.
echo ✅ Production environment started!
echo 🌐 MuseTalk API: http://localhost:8000
echo 📁 File Server: http://localhost:8080
echo 🔍 Redis: localhost:6379  
echo 🌐 Nginx Proxy: http://localhost:80
goto end

:mock
echo 🎭 Starting Mock API only...
set COMPOSE_PROFILES=mock
docker-compose up musetalk-mock-api -d
echo.
echo ✅ Mock API started!
echo 🌐 Mock API: http://localhost:8001
goto end

:full
echo 🌟 Starting all services...
set COMPOSE_PROFILES=full
docker-compose up -d
echo.
echo ✅ All services started!
echo 🌐 MuseTalk API: http://localhost:8000
echo 🌐 Mock API: http://localhost:8001  
echo 📁 File Server: http://localhost:8080
echo 🔍 Redis: localhost:6379
echo 🌐 Nginx Proxy: http://localhost:80
goto end

:stop
echo ⏹️  Stopping all services...
docker-compose down
echo ✅ All services stopped!
goto end

:clean  
echo 🧹 Stopping and cleaning up...
docker-compose down -v --remove-orphans
docker system prune -f
echo ✅ Cleanup completed!
goto end

:logs
echo 📋 Showing logs...
docker-compose logs -f
goto end

:help
echo.
echo Usage: %0 [OPTION]
echo.
echo Options:
echo   dev       Start development environment (Mock API only)  
echo   prod      Start production environment (Real API with GPU)
echo   mock      Start mock API only
echo   full      Start all services
echo   stop      Stop all services  
echo   clean     Stop and remove all containers and volumes
echo   logs      Show logs for all services
echo   help      Show this help message
echo.
echo Examples:
echo   %0 dev     # Start mock API for development
echo   %0 prod    # Start production API (requires GPU) 
echo   %0 stop    # Stop all services
echo.

:end
pause