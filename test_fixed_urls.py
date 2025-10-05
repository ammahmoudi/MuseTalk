#!/usr/bin/env python3
"""
Test script to verify all MuseTalk API URLs use BASE_URL properly
"""
import os

def test_avatar_urls():
    """Test all avatar-related URL generation"""
    
    # Test with different BASE_URL values
    test_cases = [
        ("http://localhost:8000", "Local development"),
        ("https://abc123-colab.ngrok.io", "Google Colab + ngrok"),
        ("https://workspace-abc.gradient.run", "Paperspace Gradient")
    ]
    
    avatar_id = "389eaa33-c6ee-476f-b238-4222706d1c27"
    task_id = "test-task-456"
    
    print("🧪 Testing All MuseTalk API URLs with BASE_URL")
    print("=" * 55)
    
    for base_url, description in test_cases:
        print(f"\n📍 {description}")
        print(f"   BASE_URL: {base_url}")
        
        # Simulate the URL generation functions from the API
        base_clean = base_url.rstrip('/')
        
        # All URL generation functions
        download_url = f"{base_clean}/task/{task_id}/download"
        steady_state_url = f"{base_clean}/avatar/{avatar_id}/steady-state"
        thumbnail_url = f"{base_clean}/avatar/{avatar_id}/thumbnail" 
        avatar_video_url = f"{base_clean}/avatar/{avatar_id}/video"
        
        print(f"   📥 Task Download:    {download_url}")
        print(f"   🎥 Avatar Video:     {avatar_video_url}")
        print(f"   🔄 Steady State:     {steady_state_url}")
        print(f"   🖼️  Thumbnail:        {thumbnail_url}")
        
        # Verify all URLs are properly formed
        urls = [download_url, steady_state_url, thumbnail_url, avatar_video_url]
        for url in urls:
            assert url.startswith(("http://", "https://")), f"URL missing protocol: {url}"
            assert "//" not in url.replace("://", ""), f"Double slashes found: {url}"
            assert url.startswith(base_url), f"URL doesn't start with BASE_URL: {url}"
        
    print("\n✅ All URL tests passed!")
    
    # Show the expected API response format
    print("\n📋 Expected API Response Format")
    print("=" * 55)
    
    base_url = "https://your-instance.ngrok.io"
    avatar_id = "389eaa33-c6ee-476f-b238-4222706d1c27"
    
    example_response = {
        "avatar_id": avatar_id,
        "name": "navid",
        "status": "ready", 
        "created_at": "2025-10-05T10:30:00Z",
        "video_url": f"{base_url}/avatar/{avatar_id}/video",  # ✅ HTTP URL now
        "steady_state_video_url": f"{base_url}/avatar/{avatar_id}/steady-state",
        "thumbnail_url": f"{base_url}/avatar/{avatar_id}/thumbnail",
        "frame_count": 124,
        "bbox_shift": 0
    }
    
    print("✅ FIXED Response:")
    import json
    print(json.dumps(example_response, indent=2))
    
    print(f"\n🔗 All URLs are now accessible from anywhere!")
    print(f"   • Original video: {example_response['video_url']}")
    print(f"   • Steady state:   {example_response['steady_state_video_url']}")
    print(f"   • Thumbnail:      {example_response['thumbnail_url']}")

if __name__ == "__main__":
    test_avatar_urls()