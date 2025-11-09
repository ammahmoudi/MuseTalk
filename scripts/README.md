# 🛠️ MuseTalk Scripts

This folder contains utility scripts for setup, installation, and running MuseTalk.

## Installation Scripts

- **install_dependencies.sh** - Install dependencies on Linux/Mac
- **install_dependencies.bat** - Install dependencies on Windows  
- **install_dependencies.py** - Python-based dependency installer
- **download_weights.sh** - Download model weights (Linux/Mac)
- **download_weights.bat** - Download model weights (Windows)
- **setup_online_instance.sh** - Setup script for online instances (Colab, Paperspace)

## Inference Scripts

- **inference.py** - Main inference script for video generation
- **inference.sh** - Shell wrapper for inference
- **realtime_inference.py** - Real-time inference with optimized performance
- **preprocess.py** - Video preprocessing script

## API Scripts

- **start_mock_api.bat** - Start the mock API server (Windows)
- **sync_requirements.py** - Synchronize requirements files

## Training Scripts

- **train.sh** - Training script for MuseTalk models

## Setup Directory

- **setup/** - Additional setup utilities and configurations

## Entrypoints Directory

- **entrypoints/** - Docker container entrypoint scripts for different services
  - `musetalk-mock-dev.sh` - Mock API development mode
  - `musetalk-mock-prod.sh` - Mock API production mode
  - `musetalk-real-dev.sh` - Real API development mode
  - `musetalk-real-prod.sh` - Real API production mode
  - `README.md` - Entrypoints documentation

## Usage Examples

### Install Dependencies

**Linux/Mac:**
```bash
./scripts/install_dependencies.sh
```

**Windows:**
```cmd
scripts\install_dependencies.bat
```

### Download Model Weights

**Linux/Mac:**
```bash
./scripts/download_weights.sh
```

**Windows:**
```cmd
scripts\download_weights.bat
```

### Run Inference

```bash
uv run python -m scripts.inference --config configs/inference/test.yaml
```

### Start Mock API

**Windows:**
```cmd
scripts\start_mock_api.bat
```

**Linux/Mac:**
```bash
cd api
uv run python mock_api.py
```

## Using with UV

Most scripts can be run with `uv run` for better dependency management:

```bash
# Install dependencies
uv run python scripts/install_dependencies.py

# Run inference
uv run python -m scripts.inference

# Run real-time inference
uv run python -m scripts.realtime_inference
```

## More Information

- See [Installation Guide](../docs/INSTALLATION.md) for setup instructions
- See [API Documentation](../docs/API_STREAMING_GUIDE.md) for API usage
