# MuseTalk Docker Entrypoints

This directory contains Docker entrypoint scripts for MuseTalk services.

## Available Entrypoints

### Mock API Scripts

#### `musetalk-mock-dev.sh`
- **Purpose**: Development mock API server
- **Features**:
  - Loads environment variables
  - Starts Python mock API server
  - Debug logging enabled

#### `musetalk-mock-prod.sh`
- **Purpose**: Production mock API server  
- **Features**:
  - Optimized for production deployment
  - Reduced logging overhead

### Real API Scripts

#### `musetalk-real-dev.sh`
- **Purpose**: Development real API server with CUDA
- **Features**:
  - GPU acceleration enabled
  - Development debugging
  - Hot reload capabilities

#### `musetalk-real-prod.sh`
- **Purpose**: Production real API server
- **Features**:
  - Production-optimized CUDA runtime
  - Performance tuned

## Usage

These entrypoints should be copied into the Docker container during build and used as:

```dockerfile
COPY docker/entrypoints/musetalk-mock-dev.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh
CMD ["/app/entrypoint.sh"]
```

## Requirements

- Python 3.10+ runtime
- CUDA toolkit (for real API)
- MuseTalk dependencies installed