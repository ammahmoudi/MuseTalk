#!/usr/bin/env python3
"""
Test script for MuseTalk Streaming API

This script demonstrates how to use the new streaming features for integration
with other services and real-time applications.
"""

import asyncio
import aiohttp
import base64
import json
import time
from pathlib import Path

# Configuration
API_BASE_URL = "http://localhost:8000"
TEST_AUDIO_FILE = "data/audio/yongen.wav"  # Use existing test audio
AVATAR_ID = None  # Will be set when we find an existing avatar

async def test_health_check():
    """Test the health monitoring endpoint"""
    print("🔍 Testing Health Check...")
    
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_BASE_URL}/health") as response:
            if response.status == 200:
                health = await response.json()
                print(f"✅ API Status: {health['status']}")
                print(f"📊 GPU Memory: {health.get('gpu_memory_used', 'N/A')}GB / {health.get('gpu_memory_total', 'N/A')}GB")
                print(f"🎯 Active Tasks: {health.get('active_tasks', 0)}")
                print(f"⏱️ Uptime: {health.get('uptime_seconds', 0)}s")
                return True
            else:
                print(f"❌ Health check failed: {response.status}")
                return False

async def test_metrics():
    """Test the metrics endpoint"""
    print("\n📈 Testing Metrics...")
    
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_BASE_URL}/metrics") as response:
            if response.status == 200:
                metrics = await response.json()
                print(f"✅ Total Tasks: {metrics.get('total_tasks_processed', 0)}")
                print(f"⏱️ Average Time: {metrics.get('average_processing_time', 0):.1f}s")
                print(f"🚀 Throughput: {metrics.get('throughput_fps', 0):.2f} fps")
                print(f"❌ Error Rate: {metrics.get('error_rate', 0):.2%}")
                return True
            else:
                print(f"❌ Metrics failed: {response.status}")
                return False

async def get_existing_avatar():
    """Get an existing avatar ID from the tasks list"""
    global AVATAR_ID
    
    print("\n🔍 Finding existing avatar...")
    
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_BASE_URL}/tasks") as response:
            if response.status == 200:
                tasks = await response.json()
                if tasks and len(tasks) > 0:
                    AVATAR_ID = tasks[0]["avatar_id"]
                    print(f"✅ Found avatar: {AVATAR_ID}")
                    return True
                else:
                    print("❌ No existing avatars found. Please create one first.")
                    return False
            else:
                print(f"❌ Failed to get tasks: {response.status}")
                return False

def create_audio_chunks():
    """Simulate audio chunking for streaming"""
    print("\n🎵 Creating audio chunks for streaming simulation...")
    
    # Read the test audio file
    audio_file = Path(TEST_AUDIO_FILE)
    if not audio_file.exists():
        print(f"❌ Test audio file not found: {TEST_AUDIO_FILE}")
        return []
    
    # For demonstration, we'll create fake chunks
    # In real use, you'd use actual audio processing libraries
    with open(audio_file, 'rb') as f:
        audio_data = f.read()
    
    # Split into 3 chunks for demo
    chunk_size = len(audio_data) // 3
    chunks = []
    
    for i in range(3):
        start = i * chunk_size
        end = start + chunk_size if i < 2 else len(audio_data)
        chunk_data = audio_data[start:end]
        
        chunks.append({
            "chunk_id": f"chunk_{i+1}",
            "audio_data": base64.b64encode(chunk_data).decode(),
            "sequence_number": i + 1,
            "is_final": i == 2,
            "format": "wav",
            "sample_rate": 16000
        })
    
    print(f"✅ Created {len(chunks)} audio chunks")
    return chunks

async def test_single_chunk_processing():
    """Test processing a single audio chunk"""
    if not AVATAR_ID:
        print("❌ No avatar ID available for chunk processing")
        return False
    
    print(f"\n🔄 Testing Single Chunk Processing for avatar {AVATAR_ID}...")
    
    chunks = create_audio_chunks()
    if not chunks:
        return False
    
    # Test with first chunk
    chunk_data = chunks[0]
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{API_BASE_URL}/avatar/{AVATAR_ID}/process/chunk",
            json=chunk_data
        ) as response:
            if response.status == 200:
                result = await response.json()
                print(f"✅ Chunk processed successfully!")
                print(f"📦 Task ID: {result.get('task_id', 'N/A')}")
                print(f"🎬 Status: {result.get('status', 'N/A')}")
                return True
            else:
                print(f"❌ Chunk processing failed: {response.status}")
                error_text = await response.text()
                print(f"Error: {error_text}")
                return False

async def test_batch_processing():
    """Test batch processing of multiple chunks"""
    if not AVATAR_ID:
        print("❌ No avatar ID available for batch processing")
        return False
    
    print(f"\n📦 Testing Batch Processing for avatar {AVATAR_ID}...")
    
    chunks = create_audio_chunks()
    if not chunks:
        return False
    
    request_data = {
        "audio_chunks": chunks,
        "output_format": "mp4",
        "fps": 25,
        "batch_size": 10
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{API_BASE_URL}/avatar/{AVATAR_ID}/process/batch",
            json=request_data
        ) as response:
            if response.status == 200:
                result = await response.json()
                print(f"✅ Batch processing started!")
                print(f"📦 Task ID: {result.get('task_id', 'N/A')}")
                print(f"🎬 Status: {result.get('status', 'N/A')}")
                
                # Monitor batch progress
                task_id = result.get('task_id')
                if task_id:
                    await monitor_task_progress(task_id)
                
                return True
            else:
                print(f"❌ Batch processing failed: {response.status}")
                error_text = await response.text()
                print(f"Error: {error_text}")
                return False

async def test_streaming_session():
    """Test starting a streaming session"""
    if not AVATAR_ID:
        print("❌ No avatar ID available for streaming session")
        return False
    
    print(f"\n🌊 Testing Streaming Session for avatar {AVATAR_ID}...")
    
    session_data = {
        "session_id": f"test_session_{int(time.time())}",
        "fps": 25,
        "batch_size": 5  # Smaller for real-time
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{API_BASE_URL}/avatar/{AVATAR_ID}/stream/start",
            json=session_data
        ) as response:
            if response.status == 200:
                result = await response.json()
                print(f"✅ Streaming session started!")
                print(f"🔗 Session ID: {result.get('session_id', 'N/A')}")
                print(f"🌐 WebSocket URL: {result.get('websocket_url', 'N/A')}")
                print(f"📺 Stream URL: {result.get('stream_url', 'N/A')}")
                return True
            else:
                print(f"❌ Streaming session failed: {response.status}")
                error_text = await response.text()
                print(f"Error: {error_text}")
                return False

async def monitor_task_progress(task_id: str, timeout: int = 300):
    """Monitor task progress until completion"""
    print(f"\n⏳ Monitoring task {task_id}...")
    
    start_time = time.time()
    
    async with aiohttp.ClientSession() as session:
        while time.time() - start_time < timeout:
            async with session.get(f"{API_BASE_URL}/task/{task_id}/status") as response:
                if response.status == 200:
                    status = await response.json()
                    current_status = status.get('status', 'unknown')
                    
                    if current_status == 'completed':
                        print(f"✅ Task completed successfully!")
                        print(f"⏱️ Processing time: {status.get('processing_time', 'N/A')}s")
                        print(f"📹 Output: {status.get('output_path', 'N/A')}")
                        return True
                    elif current_status == 'failed':
                        print(f"❌ Task failed: {status.get('error', 'Unknown error')}")
                        return False
                    else:
                        print(f"🔄 Status: {current_status}")
                
                await asyncio.sleep(5)  # Check every 5 seconds
        
        print(f"⏰ Task monitoring timed out after {timeout} seconds")
        return False

async def main():
    """Main test function"""
    print("🚀 MuseTalk Streaming API Test Suite")
    print("=" * 50)
    
    # Test basic endpoints
    if not await test_health_check():
        return
    
    if not await test_metrics():
        return
    
    # Get existing avatar
    if not await get_existing_avatar():
        print("💡 Tip: Create an avatar first using the /avatar/prepare endpoint")
        return
    
    # Test streaming features
    await test_single_chunk_processing()
    await test_batch_processing() 
    await test_streaming_session()
    
    print("\n🎉 All streaming API tests completed!")
    print("\n💡 Integration Tips:")
    print("   • Use single chunk processing for real-time applications")
    print("   • Use batch processing for longer audio files")
    print("   • Use streaming sessions for live applications")
    print("   • Monitor /health and /metrics for production deployments")

if __name__ == "__main__":
    asyncio.run(main())