# MuseTalk API - Avatar Media Management

## Overview
Enhanced avatar system with support for **steady state videos** and **thumbnail images** for each avatar.

## Features

### 🎥 Steady State Video
- **Purpose**: Default/idle video that plays when no audio is being processed
- **Use Cases**: 
  - Avatar idle animations
  - Breathing or subtle movement loops
  - Default state before lip-sync starts
- **Formats**: MP4, AVI, MOV, MKV

### 🖼️ Thumbnail Image
- **Purpose**: Representative image/preview for the avatar
- **Auto-Generation**: Automatically extracted from input video during preprocessing
- **Manual Upload**: Can be manually uploaded for custom thumbnails
- **Formats**: JPG, JPEG, PNG, GIF, BMP

## API Endpoints

### Avatar Preparation (Enhanced)
```http
POST /avatar/prepare
```

**Response includes new fields:**
```json
{
  "avatar_id": "abc123",
  "status": "preparing",
  "message": "Avatar preparation started...",
  "steady_state_video_url": null,
  "thumbnail_url": "https://your-api/avatar/abc123/thumbnail"
}
```

### Steady State Video Management

#### Upload Steady State Video
```http
POST /avatar/{avatar_id}/steady-state
Content-Type: multipart/form-data

video: [video file]
```

**Response:**
```json
{
  "message": "Steady state video uploaded successfully",
  "steady_state_video_url": "https://your-api/avatar/abc123/steady-state"
}
```

#### Download Steady State Video
```http
GET /avatar/{avatar_id}/steady-state
```

### Thumbnail Management

#### Upload Custom Thumbnail
```http
POST /avatar/{avatar_id}/thumbnail
Content-Type: multipart/form-data

image: [image file]
```

**Response:**
```json
{
  "message": "Thumbnail uploaded successfully", 
  "thumbnail_url": "https://your-api/avatar/abc123/thumbnail"
}
```

#### Get Thumbnail
```http
GET /avatar/{avatar_id}/thumbnail
```

**Auto-Generation**: If no thumbnail exists, it's automatically generated from the avatar video.

### Enhanced Avatar Information

#### Get Avatar Status
```http
GET /avatar/{avatar_id}/status
```

**Enhanced Response:**
```json
{
  "avatar_id": "abc123",
  "name": "My Avatar",
  "status": "ready",
  "created_at": "2025-10-05T12:00:00",
  "video_path": "/path/to/video.mp4",
  "steady_state_video_url": "https://your-api/avatar/abc123/steady-state",
  "thumbnail_url": "https://your-api/avatar/abc123/thumbnail", 
  "frame_count": 120,
  "bbox_shift": 0
}
```

#### List All Avatars
```http
GET /avatars
```

**Enhanced Response:**
```json
{
  "avatars": [
    {
      "avatar_id": "abc123",
      "name": "My Avatar",
      "status": "ready",
      "created_at": "2025-10-05T12:00:00",
      "video_path": "/path/to/video.mp4",
      "steady_state_video_url": "https://your-api/avatar/abc123/steady-state",
      "thumbnail_url": "https://your-api/avatar/abc123/thumbnail",
      "frame_count": 120,
      "bbox_shift": 0,
      "has_steady_state": true,
      "has_thumbnail": true
    }
  ],
  "count": 1
}
```

## Usage Examples

### Python Client Example
```python
import requests
import os

BASE_URL = "http://localhost:8000"  # or your ngrok URL

# 1. Prepare avatar (auto-generates thumbnail)
with open("avatar.mp4", "rb") as f:
    response = requests.post(
        f"{BASE_URL}/avatar/prepare",
        files={"video": f},
        data={"bbox_shift": 0}
    )
avatar_data = response.json()
avatar_id = avatar_data["avatar_id"]

# 2. Upload steady state video
with open("idle_animation.mp4", "rb") as f:
    requests.post(
        f"{BASE_URL}/avatar/{avatar_id}/steady-state",
        files={"video": f}
    )

# 3. Upload custom thumbnail (optional)
with open("custom_thumbnail.jpg", "rb") as f:
    requests.post(
        f"{BASE_URL}/avatar/{avatar_id}/thumbnail", 
        files={"image": f}
    )

# 4. Get avatar info with media URLs
avatar_info = requests.get(f"{BASE_URL}/avatar/{avatar_id}/status").json()
print(f"Thumbnail: {avatar_info['thumbnail_url']}")
print(f"Steady State: {avatar_info['steady_state_video_url']}")

# 5. List all avatars with media
avatars = requests.get(f"{BASE_URL}/avatars").json()
for avatar in avatars["avatars"]:
    print(f"Avatar: {avatar['name']}")
    print(f"  Has Thumbnail: {avatar['has_thumbnail']}")
    print(f"  Has Steady State: {avatar['has_steady_state']}")
```

### JavaScript/Web Example
```javascript
const BASE_URL = 'http://localhost:8000';

// Upload avatar with automatic thumbnail generation
const formData = new FormData();
formData.append('video', videoFile);
formData.append('bbox_shift', 0);

const response = await fetch(`${BASE_URL}/avatar/prepare`, {
    method: 'POST',
    body: formData
});

const avatarData = await response.json();
const avatarId = avatarData.avatar_id;

// Display thumbnail when ready
const checkStatus = async () => {
    const status = await fetch(`${BASE_URL}/avatar/${avatarId}/status`).then(r => r.json());
    
    if (status.status === 'ready') {
        // Display thumbnail
        document.getElementById('thumbnail').src = status.thumbnail_url;
        
        // Show steady state video if available
        if (status.steady_state_video_url) {
            document.getElementById('steadyState').src = status.steady_state_video_url;
        }
    }
};

// Check status every 2 seconds
const interval = setInterval(checkStatus, 2000);
```

## File Structure

Each avatar now has an organized directory structure:

```
temp/avatars/{avatar_id}/
├── input_video.mp4          # Original uploaded video
├── thumbnail.jpg            # Auto-generated or custom thumbnail
├── steady_state.mp4         # Optional steady state video
├── preprocessed/            # Extracted frames
├── realtime_materials/      # Pre-computed inference materials
└── preprocess_info.json     # Processing metadata
```

## Benefits

### 🎨 **User Experience**
- **Visual Previews**: Thumbnails provide quick avatar identification
- **Smooth Transitions**: Steady state videos create natural idle states
- **Rich Media Gallery**: Enhanced avatar listing with visual elements

### ⚡ **Performance**
- **Auto-Generation**: Thumbnails created automatically during preprocessing
- **Cached URLs**: Media served via efficient HTTP endpoints  
- **Optional Upload**: Only upload steady state videos when needed

### 🔧 **Integration**
- **Backward Compatible**: Existing API calls continue to work
- **RESTful Design**: Standard HTTP endpoints for media management
- **Base URL Support**: Works with online instances (Colab, ngrok, etc.)

## Notes

- **Thumbnails**: Automatically generated from first frame of avatar video
- **File Formats**: Common video/image formats supported
- **Storage**: Media files stored in avatar directory structure
- **URLs**: All media accessible via HTTP URLs for easy integration
- **Cleanup**: Media files deleted when avatar is deleted