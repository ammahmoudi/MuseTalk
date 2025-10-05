# 🚀 MuseTalk Installation Guide

This repository now includes comprehensive installation scripts that handle all dependencies and model downloads automatically.

## 📋 Available Installation Methods

### 1. Automated Installation (Recommended)

#### Windows:
```bash
# Run the batch script
install_dependencies.bat
```

#### Linux/Mac:
```bash
# Make executable and run
chmod +x install_dependencies.sh
./install_dependencies.sh
```

### 2. Manual Installation with UV

```bash
# Install main requirements
uv pip install -r requirements.txt

# Install API requirements  
uv pip install -r api/requirements.txt

# Install OpenMIM and MMlab packages
uv pip install openmim
mim install mmcv-full mmdet mmpose

# Install additional dependencies
uv pip install aiohttp websockets pytest black

# Download models (Linux/Mac)
./download_weights.sh

# Download models (Windows)
# download_weights.bat
```

### 3. Traditional pip installation

```bash
# Install main requirements
pip install -r requirements.txt

# Install API requirements
pip install -r api/requirements.txt

# Install OpenMIM and MMlab packages
pip install openmim
mim install mmcv-full mmdet mmpose

# Download models (Linux/Mac)
./download_weights.sh

# Download models (Windows)
# download_weights.bat
```

## 🎯 What Gets Installed

### Core Dependencies
- **PyTorch** (2.0.1) - Deep learning framework
- **NumPy** (1.23.5) - Numerical computing (compatible version)
- **OpenCV** - Computer vision library
- **Transformers** - Hugging Face transformers
- **Diffusers** - Stable Diffusion components

### API Dependencies  
- **FastAPI** - REST API framework
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation
- **aiohttp** - Async HTTP client

### MMlab Ecosystem
- **OpenMIM** - Package manager for OpenMMLab
- **MMCV** - Computer vision fundamentals
- **MMDetection** - Object detection
- **MMPose** - Human pose estimation

### Audio/Video Processing
- **librosa** - Audio analysis
- **soundfile** - Audio I/O
- **ffmpeg-python** - Video processing
- **moviepy** - Video editing

## 📥 Model Downloads

The installation automatically downloads:

### Face Detection Models
- **S3FD** - Face detection and alignment

### Pose Detection Models  
- **DWPose** - Human pose estimation for accurate face tracking

### MuseTalk Models
- **Whisper** - Audio feature extraction
- **SD-VAE** - Video generation encoder/decoder
- **UNet** - Main MuseTalk generation model

### Model Storage
```
models/
├── face_detection/
│   └── s3fd.pth
├── dwpose/
│   └── dw-ll_ucoco_384.pth
├── whisper/
│   └── [Whisper model files]
├── sd-vae/
│   └── [VAE model files]
└── musetalkV15/
    └── [MuseTalk model files]
```

## 🔧 Usage After Installation

### Start the Streaming API
```bash
python api/musetalk_native_api.py
```

### Run Realtime Inference
```bash
python scripts/realtime_inference.py --help
```

### Test Installation
```bash
python test_streaming_api.py
```

### Download Models Only
```bash
python download_models.py
```

## 🎮 Interactive Installation

Both installation scripts provide:
- ✅ **Progress tracking** with colored output
- 🔍 **Dependency verification** 
- 📦 **Package version checking**
- 🚨 **Error handling** with helpful messages
- 💡 **Next steps guidance**

## 🐛 Troubleshooting

### Common Issues

1. **GPU Memory Issues**
   - The API uses optimized memory management
   - Models are loaded globally to prevent duplication
   - `torch.no_grad()` contexts reduce memory usage

2. **NumPy Version Conflicts**
   - Scripts automatically install NumPy 1.23.5 for compatibility
   - This version works with all MMlab packages

3. **Model Download Failures**
   - The download weights scripts (`download_weights.sh` or `download_weights.bat`) can be run separately
   - Supports both Google Drive and Hugging Face downloads
   - Provides retry mechanisms and detailed error messages

4. **OpenMIM Installation Issues**
   - Make sure you have sufficient permissions
   - On some systems, you may need to restart your terminal after installation

### Manual Model Download

If automated download fails:
```bash
# Linux/Mac
./download_weights.sh

# Windows
download_weights.bat

# Or use the original scripts
./download_weights.sh    # Linux/Mac
download_weights.bat     # Windows
```

## 🎯 Ready to Use!

After installation, your MuseTalk setup includes:
- ✅ All dependencies installed with uv
- ✅ Models downloaded and ready
- ✅ Streaming API with memory optimization  
- ✅ Production-ready health monitoring
- ✅ Complete integration examples

Start with: `python api/musetalk_native_api.py` and visit `http://localhost:8000/docs` for the interactive API documentation!