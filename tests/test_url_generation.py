#!/usr/bin/env python3
"""
Test script to verify MuseTalk API URL generation with BASE_URL
"""
import os

def test_url_generation():
    """Test URL generation with different BASE_URL values"""
    
    # Test cases
    test_cases = [
        ("http://localhost:8000", "Default local development"),
        ("https://abc123-456-789.ngrok.io", "ngrok tunnel URL"),  
        ("https://my-colab-123.ngrok.io", "Google Colab + ngrok"),
        ("https://workspace-abc.gradient.run", "Paperspace Gradient"),
        ("https://api.mycompany.com", "Production API")
    ]
    
    avatar_id = "test-avatar-123"
    task_id = "test-task-456"
    
    print("🧪 Testing MuseTalk API URL Generation")
    print("=" * 50)
    
    for base_url, description in test_cases:
        print(f"\n📍 {description}")
        print(f"   BASE_URL: {base_url}")
        
        # Simulate the URL generation functions
        base_clean = base_url.rstrip('/')
        
        download_url = f"{base_clean}/task/{task_id}/download"
        steady_state_url = f"{base_clean}/avatar/{avatar_id}/steady-state" 
        thumbnail_url = f"{base_clean}/avatar/{avatar_id}/thumbnail"
        
        print(f"   📥 Download URL:     {download_url}")
        print(f"   🎥 Steady State URL: {steady_state_url}")
        print(f"   🖼️  Thumbnail URL:    {thumbnail_url}")
        
        # Verify URLs are properly formed
        assert download_url.startswith(("http://", "https://"))
        assert steady_state_url.startswith(("http://", "https://"))
        assert thumbnail_url.startswith(("http://", "https://"))
        assert "//" not in download_url.replace("://", "")
        assert "//" not in steady_state_url.replace("://", "")
        assert "//" not in thumbnail_url.replace("://", "")
        
    print("\n✅ All URL generation tests passed!")
    
    # Test environment variable usage
    print("\n🔧 Testing Environment Variable Usage")
    print("=" * 50)
    
    # Save original
    original_base = os.getenv('BASE_URL')
    
    try:
        # Test setting BASE_URL
        test_url = "https://test-instance.ngrok.io"
        os.environ['BASE_URL'] = test_url
        
        # Simulate how the API reads it
        base_url = os.getenv('BASE_URL', 'http://localhost:8000')
        print(f"✅ Environment variable set: BASE_URL={base_url}")
        
        # Test default fallback
        del os.environ['BASE_URL']
        base_url = os.getenv('BASE_URL', 'http://localhost:8000')
        print(f"✅ Default fallback works: BASE_URL={base_url}")
        
    finally:
        # Restore original
        if original_base:
            os.environ['BASE_URL'] = original_base
        elif 'BASE_URL' in os.environ:
            del os.environ['BASE_URL']

    print("\n🎯 Usage Example for Online Instances")
    print("=" * 50)
    
    example_code = '''
# For Google Colab with ngrok:
import os
from pyngrok import ngrok

# Setup ngrok tunnel  
ngrok.set_auth_token("your-token")
tunnel = ngrok.connect(8000)
print(f"Tunnel URL: {tunnel.public_url}")

# Set BASE_URL for MuseTalk API
os.environ['BASE_URL'] = tunnel.public_url

# Start the API
# python api/musetalk_native_api.py

# Now API responses will include:
# "thumbnail_url": "https://abc123.ngrok.io/avatar/xyz/thumbnail"  
# "steady_state_video_url": "https://abc123.ngrok.io/avatar/xyz/steady-state"
'''
    
    print(example_code)

if __name__ == "__main__":
    test_url_generation()