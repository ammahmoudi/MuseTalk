# 🚀 MuseTalk Legendary API

**Lightning-fast live avatar lip-sync API for real-time audio processing**

Transform your live avatar projects with blazing-fast lip synchronization! This API provides:
- ⚡ **Lightning Speed**: Optimized for real-time processing
- 🎯 **One-Time Setup**: Process video once, use for unlimited audio
- 🚀 **GPU Acceleration**: CUDA-powered performance
- 🐳 **Docker Ready**: Easy deployment with Docker Compose
- 🔄 **RESTful API**: Simple HTTP endpoints
- 📊 **Real-time Status**: Monitor processing progress

## 🎯 Perfect For Live Avatar Systems

This API is designed specifically for live avatar applications where you:
1. **Setup once**: Upload a video of your avatar
2. **Generate instantly**: Send audio and get lip-synced video in seconds
3. **Scale easily**: Handle multiple avatars and concurrent requests

## 🚀 Quick Start

### Option 1: Using UV (Recommended - Super Fast!)

```bash
# Windows
api\start_api.bat

# The script will:
# 1. Check and download models if needed
# 2. Install dependencies with UV
# 3. Start the API server
```

### Option 2: Docker (Production Ready)

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or just the API service
docker-compose up musetalk-api
```

### Option 3: Manual Setup

```bash
# 1. Install dependencies
cd api
pip install -r requirements.txt

# 2. Start the server
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 📡 API Endpoints

### 🏠 Health Check
```http
GET /
```
Check if the API is running and models are loaded.

### 🎬 Prepare Avatar (One-Time Setup)
```http
POST /avatar/prepare
Content-Type: multipart/form-data

Parameters:
- video: Video file (mp4, avi, mov, mkv)
- bbox_shift: int (optional, default=0) - Adjust mouth openness
```

**Response:**
```json
{
  "avatar_id": "uuid-string",
  "status": "preparing",
  "message": "Avatar preparation started!"
}
```

### 📊 Check Avatar Status
```http
GET /avatar/status/{avatar_id}
```

**Response:**
```json
{
  "avatar_id": "uuid-string",
  "status": "ready",  // "preparing", "ready", "error"
  "processing_progress": 100.0
}
```

### ⚡ Generate Lip-Sync (Lightning Fast!)
```http
POST /avatar/{avatar_id}/generate
Content-Type: multipart/form-data

Parameters:
- audio: Audio file (wav, mp3, m4a, flac)
```

**Response:**
```json
{
  "avatar_id": "uuid-string",
  "video_path": "/avatar/{avatar_id}/video/{audio_id}",
  "processing_time": 1.23,
  "status": "success"
}
```

### 🎥 Download Generated Video
```http
GET /avatar/{avatar_id}/video/{audio_id}
```

Returns the generated lip-synced video file.

### 🗂️ List Active Avatars
```http
GET /avatars
```

### 🗑️ Delete Avatar
```http
DELETE /avatar/{avatar_id}
```

## 🎯 Usage Example

### Python Client Example

```python
import requests
import time

API_URL = "http://localhost:8000"

# 1. Prepare avatar (one-time setup)
with open("my_avatar.mp4", "rb") as video_file:
    response = requests.post(
        f"{API_URL}/avatar/prepare",
        files={"video": video_file},
        data={"bbox_shift": 0}
    )
    avatar_id = response.json()["avatar_id"]

# 2. Wait for preparation
while True:
    status = requests.get(f"{API_URL}/avatar/status/{avatar_id}").json()
    if status["status"] == "ready":
        break
    time.sleep(2)

# 3. Generate lip-sync (super fast!)
with open("speech_audio.wav", "rb") as audio_file:
    response = requests.post(
        f"{API_URL}/avatar/{avatar_id}/generate",
        files={"audio": audio_file}
    )
    result = response.json()
    video_url = f"{API_URL}{result['video_path']}"

# 4. Download result
video_response = requests.get(video_url)
with open("lipsync_result.mp4", "wb") as f:
    f.write(video_response.content)

print(f"Generated in {result['processing_time']:.2f}s - LEGENDARY!")
```

### JavaScript/Node.js Example

```javascript
const FormData = require('form-data');
const axios = require('axios');
const fs = require('fs');

const API_URL = 'http://localhost:8000';

async function generateLipSync() {
    // 1. Prepare avatar
    const formData = new FormData();
    formData.append('video', fs.createReadStream('my_avatar.mp4'));
    formData.append('bbox_shift', '0');
    
    const avatarResponse = await axios.post(`${API_URL}/avatar/prepare`, formData, {
        headers: formData.getHeaders()
    });
    const avatarId = avatarResponse.data.avatar_id;
    
    // 2. Wait for preparation
    let status = 'preparing';
    while (status !== 'ready') {
        const statusResponse = await axios.get(`${API_URL}/avatar/status/${avatarId}`);
        status = statusResponse.data.status;
        if (status !== 'ready') {
            await new Promise(resolve => setTimeout(resolve, 2000));
        }
    }
    
    // 3. Generate lip-sync
    const audioFormData = new FormData();
    audioFormData.append('audio', fs.createReadStream('speech_audio.wav'));
    
    const generateResponse = await axios.post(
        `${API_URL}/avatar/${avatarId}/generate`, 
        audioFormData,
        { headers: audioFormData.getHeaders() }
    );
    
    console.log(`Generated in ${generateResponse.data.processing_time}s - LEGENDARY!`);
    
    // 4. Download result
    const videoResponse = await axios.get(`${API_URL}${generateResponse.data.video_path}`, {
        responseType: 'stream'
    });
    
    videoResponse.data.pipe(fs.createWriteStream('lipsync_result.mp4'));
}
```

## 🔧 Configuration

### Environment Variables

```bash
# GPU Configuration
CUDA_VISIBLE_DEVICES=0

# Model Paths (auto-detected)
MUSETALK_MODELS_DIR=./models

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=1

# Performance Tuning
TORCH_CUDA_ARCH_LIST="6.0;6.1;7.0;7.5;8.0;8.6"
```

### bbox_shift Parameter

The `bbox_shift` parameter controls mouth openness:
- **Positive values** (+1 to +20): Increase mouth openness
- **Negative values** (-1 to -20): Decrease mouth openness  
- **Default: 0**: Automatic detection

The API will tell you the valid range for your specific avatar after preparation.

## 🐳 Docker Deployment

### Basic Deployment
```bash
docker-compose up -d musetalk-api
```

### Production with Nginx
```bash
docker-compose --profile production up -d
```

### With Redis Caching (Future Feature)
```bash
docker-compose --profile with-cache up -d
```

## 📊 Performance

### Expected Performance (NVIDIA RTX 3080):
- **Avatar Preparation**: ~30-60 seconds (one-time)
- **Audio Processing**: ~1-3 seconds per 10-second audio
- **Memory Usage**: ~4-6GB VRAM
- **Concurrent Users**: 2-4 simultaneous generations

### Optimization Tips:
1. **Keep avatars prepared**: Don't delete avatars between uses
2. **Use appropriate bbox_shift**: Fine-tune for your avatar
3. **GPU Memory**: Close other GPU applications
4. **Audio Format**: WAV files process fastest

## 🔧 Troubleshooting

### Common Issues

**Models not loading:**
```bash
# Re-download models
./download_weights.bat  # Windows
./download_weights.sh   # Linux
```

**CUDA out of memory:**
```bash
# Reduce concurrent requests or use CPU
docker-compose up -e CUDA_VISIBLE_DEVICES=-1
```

**Slow processing:**
```bash
# Check GPU usage
nvidia-smi

# Ensure CUDA is available
docker-compose exec musetalk-api python -c "import torch; print(torch.cuda.is_available())"
```

## 🎯 Integration Examples

### Flask/Django Web App
```python
# In your web app
import requests

def generate_avatar_speech(avatar_id, audio_data):
    response = requests.post(
        f"http://musetalk-api:8000/avatar/{avatar_id}/generate",
        files={"audio": audio_data}
    )
    return response.json()["video_path"]
```

### Real-time Streaming
```python
# For live streaming applications
async def process_audio_stream(avatar_id, audio_chunks):
    for chunk in audio_chunks:
        # Process each audio chunk
        result = await generate_lipsync(avatar_id, chunk)
        yield result["video_path"]
```

## 📝 API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🚀 What Makes This LEGENDARY?

1. **⚡ Blazing Speed**: Pre-loaded models + optimized processing
2. **🎯 One-Time Setup**: Process avatar once, reuse forever  
3. **🔄 Real-time Ready**: Built for live avatar applications
4. **📦 Easy Deploy**: Docker + Docker Compose ready
5. **🛡️ Production Ready**: Health checks, error handling, logging
6. **🔧 Configurable**: Adjust parameters for your use case

## 🤝 Contributing

This API is built to be extended! Add features like:
- [ ] Multiple avatar formats
- [ ] Real-time audio streaming
- [ ] Batch processing
- [ ] Cloud storage integration
- [ ] Authentication & rate limiting

## 📄 License

Same as MuseTalk - MIT License for code, models available for any use.

---

**🎉 Ready to create legendary live avatars? Start the API and watch the magic happen! ⚡**