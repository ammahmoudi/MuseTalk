#!/usr/bin/env python3
"""
🚀 MuseTalk Legendary API Test Client
Test the lightning-fast lip-sync API
"""
import asyncio
import aiohttp
import json
import time
from pathlib import Path

API_BASE_URL = "http://localhost:8000"

async def test_api():
    """Test the legendary MuseTalk API! ⚡"""
    
    async with aiohttp.ClientSession() as session:
        
        print("🚀 Testing MuseTalk Legendary API...")
        
        # 1. Health Check
        print("\n1️⃣ Health Check...")
        async with session.get(f"{API_BASE_URL}/") as resp:
            health = await resp.json()
            print(f"   Status: {health['status']}")
            print(f"   Models Loaded: {health['models_loaded']}")
            print(f"   Device: {health['device']}")
        
        # 2. Prepare Avatar
        print("\n2️⃣ Preparing Avatar...")
        
        # Use test video
        video_path = Path("data/video/yongen.mp4")
        if not video_path.exists():
            print(f"   ❌ Test video not found: {video_path}")
            return
            
        with open(video_path, 'rb') as f:
            data = aiohttp.FormData()
            data.add_field('video', f, filename='test_video.mp4', content_type='video/mp4')
            data.add_field('bbox_shift', '0')
            
            async with session.post(f"{API_BASE_URL}/avatar/prepare", data=data) as resp:
                if resp.status == 200:
                    avatar_response = await resp.json()
                    avatar_id = avatar_response['avatar_id']
                    print(f"   ✅ Avatar ID: {avatar_id}")
                    print(f"   Status: {avatar_response['status']}")
                else:
                    error = await resp.text()
                    print(f"   ❌ Error: {error}")
                    return
        
        # 3. Wait for Avatar Preparation
        print("\n3️⃣ Waiting for Avatar Preparation...")
        
        while True:
            async with session.get(f"{API_BASE_URL}/avatar/status/{avatar_id}") as resp:
                status_data = await resp.json()
                status = status_data['status']
                print(f"   Status: {status}")
                
                if status == "ready":
                    print("   ✅ Avatar Ready!")
                    break
                elif status == "error":
                    print("   ❌ Avatar preparation failed!")
                    return
                    
                await asyncio.sleep(2)  # Wait 2 seconds
        
        # 4. List Avatars
        print("\n4️⃣ Listing Active Avatars...")
        async with session.get(f"{API_BASE_URL}/avatars") as resp:
            avatars_data = await resp.json()
            print(f"   Active Avatars: {avatars_data['active_avatars']}")
        
        # 5. Generate Lip-Sync
        print("\n5️⃣ Generating Lightning-Fast Lip-Sync...")
        
        audio_path = Path("data/audio/yongen.wav")
        if not audio_path.exists():
            print(f"   ❌ Test audio not found: {audio_path}")
            return
        
        start_time = time.time()
        
        with open(audio_path, 'rb') as f:
            data = aiohttp.FormData()
            data.add_field('audio', f, filename='test_audio.wav', content_type='audio/wav')
            
            async with session.post(f"{API_BASE_URL}/avatar/{avatar_id}/generate", data=data) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    generation_time = time.time() - start_time
                    
                    print(f"   ✅ Generated Successfully!")
                    print(f"   Processing Time: {result['processing_time']:.2f}s")
                    print(f"   Total Time: {generation_time:.2f}s")
                    print(f"   Video Path: {result['video_path']}")
                    
                    # 6. Download Generated Video
                    print("\n6️⃣ Downloading Generated Video...")
                    video_url = f"{API_BASE_URL}{result['video_path']}"
                    
                    async with session.get(video_url) as resp:
                        if resp.status == 200:
                            output_path = Path("test_output.mp4")
                            with open(output_path, 'wb') as f:
                                f.write(await resp.read())
                            print(f"   ✅ Video saved: {output_path}")
                        else:
                            print(f"   ❌ Download failed: {resp.status}")
                else:
                    error = await resp.text()
                    print(f"   ❌ Generation failed: {error}")
        
        print("\n🎉 API Test Complete - LEGENDARY! ⚡")

if __name__ == "__main__":
    asyncio.run(test_api())