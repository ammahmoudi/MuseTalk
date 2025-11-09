# 🐳 MuseTalk Docker Configuration

This folder contains all Docker-related files for the MuseTalk project.

## Files

### Docker Compose Files
- **docker-compose.yml** - Main Docker Compose configuration (supports multiple profiles)
- **docker-compose.dev.yml** - Development-specific configuration
- **docker-compose.prod.yml** - Production-specific configuration

### Setup Scripts
- **docker-setup.sh** - Linux/Mac Docker setup script
- **docker-setup.bat** - Windows Docker setup script
- **entrypoint.sh** - Container entrypoint script

**Note:** Specialized entrypoint scripts for different services are located in `../scripts/entrypoints/`

## Quick Start

### Using Docker Compose

```bash
# Start mock API (no GPU required)
docker-compose --profile mock up

# Start real API (requires GPU)
docker-compose --profile gpu up

# Start all services
docker-compose --profile full up
```

### Using Setup Scripts

**Linux/Mac:**
```bash
./docker-setup.sh
```

**Windows:**
```cmd
docker-setup.bat
```

## Docker Profiles

- `mock` - Mock API for development/testing
- `dev` - Development environment
- `gpu` - Real API with GPU support
- `production` - Production setup with Nginx
- `full` - All services

## Environment Variables

Configure via `.env` file in project root:
- `MUSETALK_API_PORT` - API port (default: 8000)
- `MOCK_API_PORT` - Mock API port (default: 8001)
- `CUDA_VISIBLE_DEVICES` - GPU selection (default: 0)
- `BASE_URL` - API base URL for URL generation

## More Information

See [Docker Integration Guide](../docs/DOCKER_INTEGRATION_GUIDE.md) for detailed documentation.
