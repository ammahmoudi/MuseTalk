# 🚀 MuseTalk Docker Integration Guide

This guide shows how to integrate MuseTalk API services into your external Docker Compose projects.

## Quick Start

### 1. For Development (Mock API Only)
Create a `docker-compose.yml` in your project:

```yaml
version: '3.8'

services:
  # Your application services here
  your-app:
    # ... your app configuration
    depends_on:
      - musetalk-mock
    environment:
      - MUSETALK_API_URL=http://musetalk-mock:8001

  # MuseTalk Mock API (no GPU required)
  musetalk-mock:
    image: ghcr.io/ammahmoudi/musetalk-mock:latest
    # Or build from source:
    # build:
    #   context: https://github.com/ammahmoudi/MuseTalk.git#dev-mamood
    #   dockerfile: api/Dockerfile.mock
    ports:
      - "8001:8001"
    environment:
      - BASE_URL=http://localhost:8001
    volumes:
      - musetalk_mock_temp:/app/temp

volumes:
  musetalk_mock_temp:
```

### 2. For Production (Real MuseTalk API with GPU)
```yaml
version: '3.8'

services:
  your-app:
    # ... your app configuration
    depends_on:
      - musetalk-api
    environment:
      - MUSETALK_API_URL=http://musetalk-api:8000

  # Real MuseTalk API (GPU required)
  musetalk-api:
    image: ghcr.io/ammahmoudi/musetalk-api:latest
    # Or build from source:
    # build:
    #   context: https://github.com/ammahmoudi/MuseTalk.git#dev-mamood
    #   dockerfile: api/Dockerfile.prod
    ports:
      - "8000:8000"
    environment:
      - CUDA_VISIBLE_DEVICES=0
      - BASE_URL=http://localhost:8000
    volumes:
      - ./musetalk-models:/app/models:ro  # Mount your models
      - musetalk_temp:/app/temp
      - musetalk_results:/app/results
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

volumes:
  musetalk_temp:
  musetalk_results:
```

### 3. Complete Setup with Both APIs
```yaml
version: '3.8'

services:
  your-app:
    # ... your app configuration
    depends_on:
      - musetalk-api
      - musetalk-mock
      - nginx
    environment:
      - MUSETALK_API_URL=http://nginx
      - MUSETALK_MOCK_URL=http://musetalk-mock:8001

  # Include both APIs
  musetalk-api:
    image: ghcr.io/ammahmoudi/musetalk-api:latest
    environment:
      - CUDA_VISIBLE_DEVICES=0
      - BASE_URL=http://nginx/api/v1
    volumes:
      - ./musetalk-models:/app/models:ro
      - musetalk_temp:/app/temp
      - musetalk_results:/app/results
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    networks:
      - musetalk

  musetalk-mock:
    image: ghcr.io/ammahmoudi/musetalk-mock:latest
    environment:
      - BASE_URL=http://nginx/mock
    volumes:
      - musetalk_mock_temp:/app/temp
    networks:
      - musetalk

  # Nginx proxy for routing
  nginx:
    image: nginx:alpine
    ports:
      - "8080:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - musetalk-api
      - musetalk-mock
    networks:
      - musetalk

volumes:
  musetalk_temp:
  musetalk_results:
  musetalk_mock_temp:

networks:
  musetalk:
    driver: bridge
```

## Environment Variables

### MuseTalk API
- `CUDA_VISIBLE_DEVICES`: GPU device IDs (default: "0")
- `BASE_URL`: External URL for file downloads
- `WORKERS`: Number of API workers (default: 1)

### Mock API  
- `BASE_URL`: External URL for mock responses
- `DEBUG`: Enable debug mode (true/false)

## API Endpoints

### MuseTalk API (Port 8000)
- `POST /upload_avatar` - Upload avatar video
- `POST /generate_video/{avatar_id}` - Generate lip-sync video
- `GET /avatar/{avatar_id}/status` - Check avatar status
- `GET /task/{task_id}/status` - Check task status

### Mock API (Port 8001)
- Same endpoints as real API but returns mock responses
- `GET /health` - Health check endpoint

## Volume Management

### Required Volumes
- `musetalk_temp`: Temporary processing files
- `musetalk_results`: Generated output videos  
- `musetalk_models`: Pre-trained model files (for real API)

### Model Setup
Download models before running:
```bash
# Download MuseTalk models
wget https://github.com/TMElyralab/MuseTalk/releases/download/v1.0.0/models.zip
unzip models.zip -d ./musetalk-models/
```

## Network Configuration

### Internal Communication
Services communicate via Docker network names:
- `musetalk-api:8000` - Real API
- `musetalk-mock:8001` - Mock API

### External Access
Map ports as needed:
- Production: Use nginx proxy on port 80/443
- Development: Direct port mapping

## Example Integration

### Python Client
```python
import httpx

# Use with your Docker Compose setup
MUSETALK_URL = "http://localhost:8001"  # or 8000 for real API

async def upload_avatar(video_file_path):
    async with httpx.AsyncClient() as client:
        with open(video_file_path, "rb") as f:
            response = await client.post(
                f"{MUSETALK_URL}/upload_avatar",
                files={"file": f}
            )
        return response.json()

# Example usage
avatar_data = await upload_avatar("path/to/avatar.mp4")
print(f"Avatar ID: {avatar_data['avatar_id']}")
```

### JavaScript/Node.js Client
```javascript
const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');

const MUSETALK_URL = 'http://localhost:8001';

async function uploadAvatar(videoPath) {
    const form = new FormData();
    form.append('file', fs.createReadStream(videoPath));
    
    const response = await axios.post(`${MUSETALK_URL}/upload_avatar`, form, {
        headers: form.getHeaders()
    });
    
    return response.data;
}

// Example usage
uploadAvatar('./avatar.mp4')
    .then(data => console.log('Avatar ID:', data.avatar_id))
    .catch(err => console.error('Error:', err));
```

## Troubleshooting

### Common Issues

1. **GPU not detected**: Ensure Docker has GPU support and nvidia-container-runtime
2. **Models not found**: Mount models volume correctly
3. **Permission denied**: Check file permissions in mounted volumes
4. **Port conflicts**: Adjust port mappings in your compose file

### Health Checks
```bash
# Check API health
curl http://localhost:8000/
curl http://localhost:8001/health

# Check container logs
docker logs musetalk-api
docker logs musetalk-mock
```

### Resource Requirements

#### Real MuseTalk API
- GPU: NVIDIA GPU with 4GB+ VRAM
- RAM: 8GB+ system RAM
- Storage: 10GB+ for models

#### Mock API
- CPU: Any modern CPU
- RAM: 512MB
- Storage: Minimal

## Production Recommendations

1. **Use nginx proxy** for load balancing and SSL termination
2. **Mount models as read-only** to prevent accidental modification  
3. **Configure resource limits** in Docker Compose
4. **Set up monitoring** with health checks
5. **Use secrets management** for sensitive configuration
6. **Enable logging** to persistent volumes

## Support

For issues or questions:
- GitHub Issues: https://github.com/ammahmoudi/MuseTalk/issues
- Documentation: See README.md in the repository