# 🐳 Docker Quick Start

## Prerequisites

- Docker Desktop (Windows/Mac) or Docker Engine (Linux)
- Docker Compose v2.0+
- NVIDIA Docker Runtime (for GPU support)
- 10GB+ free disk space

## Quick Commands

### Development (Mock API - No GPU Required)
```bash
# Linux/Mac
./docker-setup.sh dev

# Windows  
docker-setup.bat dev
```
Access: http://localhost:8001

### Production (Real API - GPU Required)
```bash
# Download models first
./download_weights.sh  # Linux/Mac
# or
download_weights.bat   # Windows

# Start production
./docker-setup.sh prod     # Linux/Mac  
docker-setup.bat prod      # Windows
```
Access: http://localhost:8000

### Manual Docker Compose

```bash
# Copy environment template
cp .env.example .env

# Development - Mock API only
COMPOSE_PROFILES=dev,mock,cache docker-compose up -d

# Production - Real API with GPU
COMPOSE_PROFILES=production,gpu,cache docker-compose up -d

# Stop services
docker-compose down
```

## Service Ports

| Service | Port | Description |
|---------|------|-------------|
| MuseTalk API | 8000 | Real API (GPU required) |
| Mock API | 8001 | Development API |
| File Server | 8080 | Static file serving |
| Redis Cache | 6379 | Caching service |
| Nginx Proxy | 80 | Load balancer |

## Environment Variables

Key variables in `.env`:
- `MUSETALK_API_PORT=8000` - Real API port
- `MOCK_API_PORT=8001` - Mock API port  
- `CUDA_VISIBLE_DEVICES=0` - GPU selection
- `COMPOSE_PROFILES=dev,mock` - Active services

## Integration in External Projects

See [DOCKER_INTEGRATION_GUIDE.md](DOCKER_INTEGRATION_GUIDE.md) for detailed examples.

### Basic External Integration
```yaml
# In your project's docker-compose.yml
version: '3.8'
services:
  your-app:
    # your app config
    depends_on: [musetalk-mock]
    
  musetalk-mock:
    image: ghcr.io/ammahmoudi/musetalk-mock:latest
    ports: ["8001:8001"]
```

## Volumes

- `musetalk_temp` - Temporary processing files
- `musetalk_results` - Generated videos
- `musetalk_models` - AI model files  
- `redis_data` - Cache storage

## Troubleshooting

### Common Issues
- **GPU not found**: Install nvidia-container-runtime
- **Models missing**: Run `download_weights.sh/bat` first  
- **Permission errors**: Check volume mount permissions
- **Port conflicts**: Adjust ports in `.env`

### Health Checks
```bash
curl http://localhost:8000/     # Real API
curl http://localhost:8001/health  # Mock API
```

### View Logs
```bash
docker-compose logs -f musetalk-api
docker-compose logs -f musetalk-mock-api
```

For complete documentation, see [DOCKER_INTEGRATION_GUIDE.md](DOCKER_INTEGRATION_GUIDE.md).