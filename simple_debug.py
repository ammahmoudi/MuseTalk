#!/usr/bin/env python3
"""
Simple debug script for avatar endpoints (no external dependencies)
"""
import urllib.request
import urllib.error
import json

def test_avatar_debug(base_url, avatar_id):
    """Test avatar debug endpoint"""
    try:
        debug_url = f"{base_url}/avatar/{avatar_id}/debug"
        print(f"🔍 Testing debug endpoint: {debug_url}")
        
        with urllib.request.urlopen(debug_url) as response:
            data = json.loads(response.read().decode())
            
        print("📊 Debug Information:")
        print(f"  Avatar ID: {data['avatar_id']}")
        print(f"  Avatar Dir Exists: {data['avatar_dir_exists']}")
        print(f"  Video Path Exists: {data['video_path_exists']}")
        print(f"  Steady State Path: {data['steady_state_path']}")
        print(f"  Steady State Exists: {data['steady_state_exists']}")
        print(f"  Thumbnail Path: {data['thumbnail_path']}")
        print(f"  Thumbnail Exists: {data['thumbnail_exists']}")
        
        print("\n📁 Files in avatar directory:")
        for file_path in data['files_in_dir']:
            print(f"  - {file_path}")
            
        print("\n🔗 Generated URLs:")
        for url_type, url in data['generated_urls'].items():
            print(f"  {url_type}: {url}")
            
        return data
        
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP Error {e.code}: {e.reason}")
        print(f"   URL: {debug_url}")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_endpoint_access(base_url, avatar_id):
    """Test if individual endpoints are accessible"""
    endpoints = {
        "avatar_video": f"{base_url}/avatar/{avatar_id}/video",
        "steady_state": f"{base_url}/avatar/{avatar_id}/steady-state", 
        "thumbnail": f"{base_url}/avatar/{avatar_id}/thumbnail"
    }
    
    print("\n🧪 Testing endpoint accessibility:")
    for name, url in endpoints.items():
        try:
            req = urllib.request.Request(url, method='HEAD')  # HEAD request to check existence
            with urllib.request.urlopen(req) as response:
                print(f"  ✅ {name}: {response.status} - {url}")
        except urllib.error.HTTPError as e:
            print(f"  ❌ {name}: {e.code} {e.reason} - {url}")
        except Exception as e:
            print(f"  ❌ {name}: Error - {e}")

if __name__ == "__main__":
    # Configuration
    base_url = "http://143.55.45.86:54724"
    avatar_id = "389eaa33-c6ee-476f-b238-4222706d1c27"
    
    print("🔍 MuseTalk Avatar Debug Tool")
    print("=" * 40)
    
    # Test debug endpoint
    debug_data = test_avatar_debug(base_url, avatar_id)
    
    # Test individual endpoints
    if debug_data:
        test_endpoint_access(base_url, avatar_id)
        
        # Analysis
        print("\n📋 Analysis:")
        if not debug_data['steady_state_exists']:
            print("  ⚠️  No steady state video uploaded - use POST /avatar/{id}/steady-state to upload one")
        if not debug_data['thumbnail_exists']:
            print("  ⚠️  No thumbnail found - should auto-generate during preprocessing")
        if debug_data['video_path_exists']:
            print("  ✅ Original avatar video exists")
        else:
            print("  ❌ Original avatar video missing!")
            
    print(f"\n💡 To upload steady state video:")
    print(f"   curl -X POST {base_url}/avatar/{avatar_id}/steady-state -F 'video=@your_steady_state.mp4'")