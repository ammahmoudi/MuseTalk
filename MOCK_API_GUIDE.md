# 🎭 MuseTalk Mock API - Development & Testing

## 🚀 Quick Start

The Mock API provides instant responses with fake data, perfect for:
- Frontend development without GPU processing
- API integration testing  
- Demo purposes
- Development without model dependencies

## 📁 Test Assets Directory Structure

```
test_assets/
├── avatars/          # Sample avatar videos 
├── videos/           # 🔥 TEST VIDEOS FOR MOCK RESULTS (IMPORTANT!)
├── thumbnails/       # Sample thumbnail images
├── steady_state/     # Sample steady state videos
├── results/          # Generated mock results (auto-created)
├── temp_audio/       # Temporary user audio files (auto-created)
```

**🎬 Key:** Place good quality videos in `test_assets/videos/` - these will be used with your audio!

## 🎬 Where to Put Test Videos

### 1. **Avatar Videos** → `test_assets/avatars/`
```bash
# Place sample avatar videos here:
test_assets/avatars/sample_avatar.mp4
test_assets/avatars/john_doe.mp4
test_assets/avatars/jane_smith.mp4
```

### 2. **🔥 Test Videos for Mock Results** → `test_assets/videos/`
```bash
# Place HIGH QUALITY videos here for mock generation:
test_assets/videos/talking_person.mp4
test_assets/videos/avatar_demo.mp4
test_assets/videos/sample_person.mp4

# These videos will be combined with YOUR audio!
# Video length automatically adjusted to match audio duration
```

### 3. **Steady State Videos** → `test_assets/steady_state/`
```bash
# Place ANY video file here (any name works):
test_assets/steady_state/my_idle_video.mp4
test_assets/steady_state/breathing.avi
test_assets/steady_state/any_name_works.mov

# Mock API will use any video file it finds in this folder
```

### 4. **Thumbnails** → `test_assets/thumbnails/`
```bash
# Place ANY image file here (any name works):
test_assets/thumbnails/my_thumbnail.jpg
test_assets/thumbnails/avatar_preview.png
test_assets/thumbnails/any_image.jpeg

# Mock API will use any image file it finds in this folder
```

## 🏃‍♂️ Running the Mock API

### Start Mock API (Port 8001)
```bash
# Start mock API
python api/mock_api.py

# Mock API will be available at:
# http://localhost:8001
```

### Start Real API (Port 8000) 
```bash
# Start real API in parallel
python api/musetalk_native_api.py

# Real API will be available at:
# http://localhost:8000
```

## 🎯 Mock API Features

### ✅ **Realistic Results**

- **Real Audio Processing**: Uses your input audio with test videos
- **ffmpeg Integration**: Combines user audio with avatar videos  
- **Authentic Results**: Download contains your audio, not fake data
- Avatar preparation: ~2 seconds (fake processing)
- Video generation: ~3-4 seconds (real audio processing)

### ✅ **Smart Simulation**

- Status updates (queued → processing → completed)
- Realistic processing times with actual file operations
- Proper HTTP responses and error handling
- Fallback to test videos if ffmpeg unavailable

### ✅ **Flexible Test Data**

- Uses existing avatars from `temp/avatars/`
- Combines your audio with avatar videos
- Serves generated results from `test_assets/results/`
- Creates fake avatars if none exist

### ✅ **Health & Debug Endpoints**
```bash
# Health check for monitoring
GET /health

# Basic status
GET /

# Debug avatars
GET /debug/avatars

# Debug tasks  
GET /debug/tasks

# Create instant test avatar
POST /debug/create-test-avatar?name=MyTestAvatar
```

## 📋 API Endpoints (Same as Real API)

### Avatar Management
```bash
POST /avatar/prepare              # Upload avatar (fake processing)
GET  /avatar/{id}/status          # Avatar status
GET  /avatars                     # List all avatars
```

### Video Generation
```bash
POST /avatar/{id}/generate        # Generate video (fake processing)  
GET  /task/{id}/status           # Task status
GET  /tasks                      # List all tasks
```

### File Downloads
```bash
GET /avatar/{id}/video           # Original avatar video
GET /avatar/{id}/steady-state    # Steady state video
GET /avatar/{id}/thumbnail       # Thumbnail image
GET /task/{id}/download          # Generated result video
```

## 🧪 Testing Examples

### Test Avatar Preparation
```bash
curl -X POST "http://localhost:8001/avatar/prepare" \
  -F "video=@test_video.mp4" \
  -F "bbox_shift=0"

# Response (instant):
{
  "avatar_id": "abc123...",
  "status": "preparing",
  "message": "🎭 Mock avatar preparation started!",
  "steady_state_video_url": "http://localhost:8001/avatar/abc123/steady-state",
  "thumbnail_url": "http://localhost:8001/avatar/abc123/thumbnail"
}
```

### Test Video Generation
```bash
curl -X POST "http://localhost:8001/avatar/abc123/generate" \
  -F "audio=@test_audio.wav"

# Response (instant):
{
  "task_id": "def456...",
  "avatar_id": "abc123...",
  "status": "queued", 
  "message": "🎭 Mock video generation started!"
}
```

### Check Status
```bash
# Check avatar status
curl "http://localhost:8001/avatar/abc123/status"

# Check task status  
curl "http://localhost:8001/task/def456/status"
```

## 🔧 Configuration

### Environment Variables
```bash
# Set custom base URL for mock API (for online instances)
export BASE_URL="https://your-mock-instance.ngrok.io"

# Start mock API
python api/mock_api.py

# All URLs will use the BASE_URL:
# - Download URLs: https://your-instance.ngrok.io/task/{id}/download
# - Avatar URLs: https://your-instance.ngrok.io/avatar/{id}/video
# - Steady state: https://your-instance.ngrok.io/avatar/{id}/steady-state
```

### Using Existing Avatars
The mock API automatically detects existing avatars in `temp/avatars/` and creates mock data for them.

## 💡 Development Tips

### 1. **Parallel Development**
```bash
# Terminal 1: Real API
python api/musetalk_native_api.py  # Port 8000

# Terminal 2: Mock API  
python api/mock_api.py             # Port 8001
```

### 2. **Frontend Integration**
```javascript
// Switch between real and mock API
const API_BASE = process.env.NODE_ENV === 'development' 
  ? 'http://localhost:8001'  // Mock API
  : 'http://localhost:8000'  // Real API

// All endpoints work the same!
fetch(`${API_BASE}/avatars`)
```

### 3. **Testing Workflows**
```bash
# Test complete workflow with mock API
1. POST /avatar/prepare        # 2 seconds
2. GET  /avatar/{id}/status    # Check ready
3. POST /avatar/{id}/generate  # 3-4 seconds  
4. GET  /task/{id}/status      # Check completed
5. GET  /task/{id}/download    # Download result
```

## 🎪 Demo Mode

### Create Instant Test Avatars
```bash
curl -X POST "http://localhost:8001/debug/create-test-avatar?name=Demo%20Avatar"

# Instantly creates a ready avatar with fake data!
```

### Populate Test Data
```bash
# The mock API will create 4 fake avatars on startup if none exist:
# - John Doe (124 frames)
# - Jane Smith (89 frames)  
# - Bob Wilson (156 frames)
# - Alice Johnson (203 frames)
```

Perfect for demos, development, and testing! 🎉