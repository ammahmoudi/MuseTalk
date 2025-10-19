#!/usr/bin/env python3
"""
🎭 MuseTalk Mock API Test Script

Quick test to demonstrate mock API functionality.
Run this after starting the mock API server.
"""

import requests
import json
import time
from pathlib import Path

# Mock API Configuration
MOCK_API_BASE = "http://localhost:8001"
TEST_ASSETS = Path(__file__).parent.parent / "test_assets"

def test_mock_api():
    """Test the mock API functionality"""
    print("🎭 MuseTalk Mock API Test")
    print("=" * 50)
    
    try:
        # Test 1: Check server health
        print("1️⃣ Testing server health...")
        response = requests.get(f"{MOCK_API_BASE}/")
        if response.status_code == 200:
            print("✅ Mock API server is running!")
            data = response.json()
            print(f"   Message: {data.get('message', 'N/A')}")
        else:
            print("❌ Mock API server not responding")
            return
        
        # Test 1.5: Check detailed health status
        print("\n🔍 Checking detailed health status...")
        response = requests.get(f"{MOCK_API_BASE}/health")
        if response.status_code == 200:
            health = response.json()
            print("✅ Health check successful!")
            print(f"   Status: {health.get('status', 'N/A')}")
            print(f"   FFmpeg: {'✅' if health.get('dependencies', {}).get('ffmpeg_available') else '❌'}")
            print(f"   Test videos: {health.get('test_assets', {}).get('test_videos_count', 0)}")
            print(f"   Avatars: {health.get('mock_data', {}).get('avatars_count', 0)}")
        else:
            print("⚠️ Health check failed, but continuing test...")
        
        # Test 2: List existing avatars
        print("\n2️⃣ Listing existing avatars...")
        response = requests.get(f"{MOCK_API_BASE}/avatars")
        if response.status_code == 200:
            avatars = response.json()
            print(f"✅ Found {len(avatars)} existing avatars:")
            for avatar in avatars[:3]:  # Show first 3
                print(f"   - {avatar['name']} ({avatar['frame_count']} frames)")
                if len(avatars) > 3:
                    print(f"   ... and {len(avatars) - 3} more")
                break
        
        # Test 3: Create instant test avatar
        print("\n3️⃣ Creating instant test avatar...")
        response = requests.post(f"{MOCK_API_BASE}/debug/create-test-avatar?name=Quick%20Test%20Avatar")
        if response.status_code == 200:
            test_avatar = response.json()
            print("✅ Instant avatar created!")
            print(f"   Avatar ID: {test_avatar['avatar_id']}")
            print(f"   Name: {test_avatar['name']}")
            print(f"   Status: {test_avatar['status']}")
            
            avatar_id = test_avatar['avatar_id']
            
            # Test 4: Generate mock video with real audio processing
            print("\n4️⃣ Starting mock video generation with audio...")
            # Create a simple WAV file header for more realistic test
            wav_header = b'RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00D\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00'
            mock_audio_content = wav_header + b'\x00' * 1000  # Add some audio data
            files = {'audio': ('test_audio.wav', mock_audio_content, 'audio/wav')}
            
            response = requests.post(f"{MOCK_API_BASE}/avatar/{avatar_id}/generate", files=files)
            if response.status_code == 200:
                task = response.json()
                print("✅ Mock video generation with user audio started!")
                print(f"   Task ID: {task['task_id']}")
                print(f"   Status: {task['status']}")
                print(f"   Message: {task['message']}")
                
                task_id = task['task_id']
                
                # Test 5: Monitor task progress
                print("\n5️⃣ Monitoring task progress...")
                for i in range(6):  # Check for 6 seconds (mock processing takes ~3-4 seconds)
                    time.sleep(1)
                    response = requests.get(f"{MOCK_API_BASE}/task/{task_id}/status")
                    if response.status_code == 200:
                        status = response.json()
                        print(f"   Status check {i+1}: {status['status']}")
                        
                        if status['status'] == 'completed':
                            print("✅ Mock video generation completed!")
                            print(f"   Download URL: {status.get('output_path', 'N/A')}")
                            print("   Result contains your audio combined with test video!")
                            print("   You can download it from the URL above!")
                            break
                        elif status['status'] == 'failed':
                            print("❌ Mock video generation failed")
                            break
                    else:
                        print("❌ Failed to check task status")
                        break
        
        # Test 6: List all tasks
        print("\n6️⃣ Listing all tasks...")
        response = requests.get(f"{MOCK_API_BASE}/tasks")
        if response.status_code == 200:
            tasks = response.json()
            print(f"✅ Found {len(tasks)} tasks in mock system")
        
        print("\n🎉 Mock API test completed!")
        print("\nNext steps:")
        print("- Start mock API: python api/mock_api.py")
        print("- Test with your frontend: Use http://localhost:8001 as API base")
        print("- Add test videos to test_assets/ folders")
        print("- Use debug endpoints for instant test data")
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Mock API server")
        print("Make sure to start the mock API server first:")
        print("   python api/mock_api.py")
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_mock_api()