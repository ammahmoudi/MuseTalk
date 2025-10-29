#!/bin/bash
# 🚀 MuseTalk Docker Quick Setup Script

set -e

echo "🚀 MuseTalk Docker Setup"
echo "======================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ Created .env file. You can edit it to customize settings."
else
    echo "✅ .env file already exists."
fi

# Function to show usage
show_usage() {
    echo ""
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  dev       Start development environment (Mock API only)"
    echo "  prod      Start production environment (Real API with GPU)"
    echo "  mock      Start mock API only"
    echo "  full      Start all services"
    echo "  stop      Stop all services"
    echo "  clean     Stop and remove all containers and volumes"
    echo "  logs      Show logs for all services"
    echo "  help      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 dev     # Start mock API for development"
    echo "  $0 prod    # Start production API (requires GPU)"
    echo "  $0 stop    # Stop all services"
    echo ""
}

# Parse command line arguments
case "${1:-help}" in
    "dev")
        echo "🔧 Starting development environment (Mock API)..."
        COMPOSE_PROFILES=dev,mock,cache docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
        echo ""
        echo "✅ Development environment started!"
        echo "🌐 Mock API: http://localhost:8001"
        echo "🔍 Redis: localhost:6379"
        ;;
    
    "prod")
        echo "🚀 Starting production environment (Real API with GPU)..."
        # Check if models exist
        if [ ! -d "./models/musetalk" ]; then
            echo "⚠️  Warning: MuseTalk models not found in ./models/"
            echo "   Please download models first or the API will not work."
            echo "   Run: ./download_weights.sh"
        fi
        
        COMPOSE_PROFILES=production,gpu,cache,files docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
        echo ""
        echo "✅ Production environment started!"
        echo "🌐 MuseTalk API: http://localhost:8000"
        echo "📁 File Server: http://localhost:8080"
        echo "🔍 Redis: localhost:6379"
        echo "🌐 Nginx Proxy: http://localhost:80"
        ;;
    
    "mock")
        echo "🎭 Starting Mock API only..."
        COMPOSE_PROFILES=mock docker-compose up musetalk-mock-api -d
        echo ""
        echo "✅ Mock API started!"
        echo "🌐 Mock API: http://localhost:8001"
        ;;
    
    "full")
        echo "🌟 Starting all services..."
        COMPOSE_PROFILES=full docker-compose up -d
        echo ""
        echo "✅ All services started!"
        echo "🌐 MuseTalk API: http://localhost:8000"
        echo "🌐 Mock API: http://localhost:8001"
        echo "📁 File Server: http://localhost:8080"
        echo "🔍 Redis: localhost:6379"
        echo "🌐 Nginx Proxy: http://localhost:80"
        ;;
    
    "stop")
        echo "⏹️  Stopping all services..."
        docker-compose down
        echo "✅ All services stopped!"
        ;;
    
    "clean")
        echo "🧹 Stopping and cleaning up..."
        docker-compose down -v --remove-orphans
        docker system prune -f
        echo "✅ Cleanup completed!"
        ;;
    
    "logs")
        echo "📋 Showing logs..."
        docker-compose logs -f
        ;;
    
    "help"|*)
        show_usage
        ;;
esac