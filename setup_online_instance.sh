#!/bin/bash

# MuseTalk API - Online Instance Configuration Script
# This script helps you configure the API for online instances like Google Colab, Paperspace, etc.

echo "🚀 MuseTalk API Online Instance Setup"
echo "=====================================

# Step 1: Set the BASE_URL environment variable
# Replace 'your-instance-url' with your actual instance URL (ngrok, Colab, etc.)

echo "📝 Setting up environment for online instance..."

# Example configurations:

# For Google Colab with ngrok:
# export BASE_URL="https://abc123-4567-8901-2345.ngrok.io"

# For Paperspace Gradient:
# export BASE_URL="https://your-paperspace-url.gradient.run"

# For other cloud instances:
# export BASE_URL="https://your-cloud-instance-url.com"

echo "
🔧 Configuration Instructions:

1. **Set BASE_URL environment variable:**
   export BASE_URL='https://your-instance-url'

2. **For Google Colab + ngrok:**
   - Install ngrok: !pip install pyngrok
   - Start ngrok tunnel: from pyngrok import ngrok; ngrok.set_auth_token('your-token'); tunnel = ngrok.connect(8000)
   - Set BASE_URL to the ngrok URL

3. **Start the API:**
   python api/musetalk_native_api.py
   # or 
   python api/main.py

4. **Test the configuration:**
   curl \$BASE_URL/

📋 Example usage in code:
```python
import os

# Set before starting the API
os.environ['BASE_URL'] = 'https://your-instance-url'

# Now the API will return proper URLs like:
# https://your-instance-url/task/abc123/download
# instead of local paths like:
# /workspace/MuseTalk/temp/avatars/abc123/output.mp4
```

⚠️  **Important Notes:**

1. **Security**: Never expose your API publicly without authentication in production
2. **CORS**: The API allows all origins - configure properly for production
3. **File Access**: Generated videos will be accessible via HTTP download URLs
4. **Storage**: Clean up old avatars and tasks periodically to save disk space

🔗 **URL Format Changes:**

❌ **Before (local paths - not accessible):**
/workspace/MuseTalk/temp/avatars/d23ccd81.../output/34760b99....mp4

✅ **After (HTTP URLs - accessible):**
https://your-instance-url/task/34760b99.../download

"

echo "✅ Configuration guide complete!"
echo "Don't forget to set BASE_URL environment variable before starting the API!"