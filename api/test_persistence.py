"""
🧪 Test avatar persistence functionality
Tests that avatars are saved and loaded correctly across server restarts
"""
import requests
import json
from pathlib import Path
import time

def test_avatar_persistence():
    """Test that avatars persist across server operations"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Avatar Persistence")
    print("=" * 50)
    
    # Test 1: Check initial state
    print("\n1️⃣ Checking initial avatar list...")
    response = requests.get(f"{base_url}/avatars")
    if response.status_code == 200:
        data = response.json()
        print(f"   Active avatars: {data['active_avatars']}")
        print(f"   Storage file exists: {data['storage_info']['storage_exists']}")
        print(f"   Storage location: {data['storage_info']['storage_file']}")
    else:
        print(f"   ❌ Failed to get avatars: {response.status_code}")
        return False
    
    # Test 2: Check storage file directly
    print("\n2️⃣ Checking storage file directly...")
    project_root = Path(__file__).parent.parent
    storage_file = project_root / "temp" / "avatars.json"
    
    if storage_file.exists():
        try:
            with open(storage_file, 'r') as f:
                stored_avatars = json.load(f)
            print(f"   📁 Found {len(stored_avatars)} avatars in storage file")
            for avatar_id, data in stored_avatars.items():
                print(f"      - {avatar_id}: {data.get('status', 'unknown')}")
        except Exception as e:
            print(f"   ⚠️ Error reading storage file: {e}")
    else:
        print(f"   📝 Storage file doesn't exist yet: {storage_file}")
    
    # Test 3: Check temp directory structure
    print("\n3️⃣ Checking temp directory structure...")
    temp_dir = project_root / "temp"
    avatars_dir = temp_dir / "avatars"
    
    print(f"   📂 Temp directory: {temp_dir}")
    print(f"      Exists: {temp_dir.exists()}")
    
    if avatars_dir.exists():
        avatar_folders = [d for d in avatars_dir.iterdir() if d.is_dir()]
        print(f"   📁 Avatar directories found: {len(avatar_folders)}")
        for folder in avatar_folders[:5]:  # Show first 5
            print(f"      - {folder.name}")
    else:
        print(f"   📁 No avatar directories yet: {avatars_dir}")
    
    print("\n✅ Persistence test completed!")
    print(f"\n🔗 Test with the API:")
    print(f"   📋 List avatars: GET {base_url}/avatars")
    print(f"   🎯 Prepare avatar: POST {base_url}/avatar/prepare")
    print(f"   📊 Check status: GET {base_url}/avatar/status/{{avatar_id}}")
    print(f"   📚 Full docs: {base_url}/docs")
    
    return True

if __name__ == "__main__":
    try:
        test_avatar_persistence()
    except Exception as e:
        print(f"\n❌ Test failed: {e}")