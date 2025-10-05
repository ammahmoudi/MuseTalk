# MuseTalk API - Online Instance Configuration

## Problem
When running MuseTalk API on online instances (Google Colab, Paperspace, etc.), the API returns local file paths that are not accessible from outside the container:

```
❌ Local path (not accessible):
/workspace/MuseTalk/temp/avatars/d23ccd81-d649-4e00-93c9-7693a8a9a3b2/output/34760b99-6d7c-4227-ba69-f2937c6e6b00.mp4
```

## Solution
Configure the `BASE_URL` environment variable to make the API return proper HTTP download URLs:

```
✅ HTTP URL (accessible):
https://your-instance-url.ngrok.io/task/34760b99-6d7c-4227-ba69-f2937c6e6b00/download
```

## Setup Instructions

### 1. Set Environment Variable
```bash
export BASE_URL="https://your-instance-url"
```

### 2. Google Colab + ngrok Setup
```python
# Install and setup ngrok
!pip install pyngrok
from pyngrok import ngrok
import os

# Set your ngrok auth token
ngrok.set_auth_token("your-ngrok-auth-token")

# Start tunnel on port 8000
tunnel = ngrok.connect(8000)
print(f"Public URL: {tunnel.public_url}")

# Set BASE_URL for the API
os.environ['BASE_URL'] = tunnel.public_url

# Now start the API
!python api/musetalk_native_api.py
```

### 3. Paperspace Gradient
```python
import os
os.environ['BASE_URL'] = "https://your-paperspace-url.gradient.run"
```

### 4. Other Cloud Platforms
```python
import os
os.environ['BASE_URL'] = "https://your-cloud-instance-url.com"
```

## API Endpoints

### File Download Endpoints
Both API versions now support proper file serving:

**musetalk_native_api.py:**
- `GET /task/{task_id}/download` - Download generated video

**main.py:**
- `GET /avatar/{avatar_id}/video/{audio_id}` - Download generated video

### Response Format Changes

**Before:**
```json
{
    "task_id": "abc123",
    "status": "completed", 
    "output_path": "/workspace/MuseTalk/temp/avatars/.../output.mp4"
}
```

**After (with BASE_URL set):**
```json
{
    "task_id": "abc123",
    "status": "completed",
    "output_path": "https://your-instance-url.ngrok.io/task/abc123/download"
}
```

## Testing the Configuration

```bash
# Test health endpoint
curl $BASE_URL/

# Generate a video
curl -X POST "$BASE_URL/avatar/{avatar_id}/generate" \
     -F "audio=@audio.wav"

# The response will now contain accessible URLs!
```

## Important Notes

1. **Security**: Configure authentication for production use
2. **CORS**: API allows all origins by default - secure for production  
3. **Cleanup**: Periodically clean old files to manage disk space
4. **Performance**: File downloads go through the API server (consider CDN for high traffic)

## Troubleshooting

### URLs still showing local paths?
- Ensure `BASE_URL` environment variable is set before starting the API
- Restart the API after setting the environment variable

### Files not downloading?
- Check that the file exists: `GET /task/{task_id}/status`
- Verify the task completed successfully
- Ensure proper permissions on the results directory

### ngrok tunnel issues?
- Verify your ngrok auth token is correct
- Check ngrok tunnel status: `ngrok http 8000 --log=stdout`
- Try a different port if 8000 is busy