#!/usr/bin/env python3
"""
Debug script to test avatar endpoints and find why they're returning 404
"""
import requests
import json

# Your server details
BASE_URL = "http://143.55.45.86:54724"
AVATAR_ID = "389eaa33-c6ee-476f-b238-4222706d1c27"

def test_avatar_endpoints():
    """Test all avatar endpoints to find the issue"""
    
    print("🔍 Debugging Avatar Endpoints")
    print("=" * 50)
    print(f"Server: {BASE_URL}")
    print(f"Avatar ID: {AVATAR_ID}")
    print()
    
    # Test 1: Check if API is running
    print("1️⃣ Testing API health...")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=10)
        print(f"   ✅ API is running: {response.status_code}")
    except Exception as e:
        print(f"   ❌ API not accessible: {e}")
        return
    
    # Test 2: Check debug endpoint  
    print("2️⃣ Testing avatar debug endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/avatar/{AVATAR_ID}/debug", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            debug_data = response.json()
            print("   📊 Debug Data:")
            print(json.dumps(debug_data, indent=4))
        else:
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Debug endpoint error: {e}")
    
    print()
    
    # Test 3: Check avatar status
    print("3️⃣ Testing avatar status endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/avatar/{AVATAR_ID}/status", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            status_data = response.json()
            print("   📋 Avatar Status:")
            print(json.dumps(status_data, indent=4))
        else:
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Status endpoint error: {e}")
    
    print()
    
    # Test 4: List all avatars
    print("4️⃣ Testing list avatars endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/avatars", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            avatars_data = response.json()
            print(f"   📝 Found {avatars_data.get('count', 0)} avatars")
            if avatars_data.get('avatars'):
                for avatar in avatars_data['avatars']:
                    print(f"      - {avatar.get('avatar_id', 'Unknown')}: {avatar.get('status', 'Unknown')}")
        else:
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ List avatars error: {e}")
    
    print()
    
    # Test 5: Test specific avatar endpoints
    endpoints_to_test = [
        ("video", f"{BASE_URL}/avatar/{AVATAR_ID}/video"),
        ("steady-state", f"{BASE_URL}/avatar/{AVATAR_ID}/steady-state"), 
        ("thumbnail", f"{BASE_URL}/avatar/{AVATAR_ID}/thumbnail")
    ]
    
    print("5️⃣ Testing avatar media endpoints...")
    for name, url in endpoints_to_test:
        try:
            response = requests.get(url, timeout=10)
            print(f"   {name}: {response.status_code}")
            if response.status_code != 200:
                print(f"      Error: {response.text}")
        except Exception as e:
            print(f"   {name}: Error - {e}")

if __name__ == "__main__":
    test_avatar_endpoints()