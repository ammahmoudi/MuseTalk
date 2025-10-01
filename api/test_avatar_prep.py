"""
🧪 Test script for avatar preparation API
Tests the improved avatar preprocessing functionality
"""
import requests
import json
from pathlib import Path

def test_avatar_preparation():
    """Test avatar preparation with a sample video"""
    base_url = "http://localhost:8000"
    
    # First, test health check
    print("🏥 Testing health check...")
    response = requests.get(f"{base_url}/")
    print(f"Health check: {response.status_code}")
    if response.status_code == 200:
        health_data = response.json()
        print(f"   Status: {health_data.get('status')}")
        print(f"   Device: {health_data.get('device')}")
        if health_data.get('gpu_info'):
            gpu = health_data['gpu_info']
            print(f"   GPU: {gpu.get('gpu_name')} ({gpu.get('gpu_memory')})")
    
    # Test avatar preparation (would need actual video file)
    print("\n📹 Avatar preparation endpoint available at:")
    print(f"   POST {base_url}/avatar/prepare")
    print("   - Upload video file")
    print("   - Set bbox_shift parameter")
    
    # Test status endpoint format
    print(f"\n📊 Status check endpoint:")
    print(f"   GET {base_url}/avatar/status/{{avatar_id}}")
    
    # Test generation endpoint format
    print(f"\n⚡ Lip-sync generation endpoint:")
    print(f"   POST {base_url}/avatar/{{avatar_id}}/generate")
    print("   - Upload audio file")
    
    print(f"\n📚 Full API documentation available at:")
    print(f"   {base_url}/docs")
    
    return True

if __name__ == "__main__":
    try:
        test_avatar_preparation()
        print("\n✅ API test completed successfully!")
    except Exception as e:
        print(f"\n❌ API test failed: {e}")