"""
🚀 MuseTalk API Client Examples
Examples showing how to integrate MuseTalk API with other services for streaming
"""
import asyncio
import aiohttp
import websockets
import json
import base64
import time
from pathlib import Path
from typing import List, Optional


class MuseTalkClient:
    """Client for integrating with MuseTalk API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def health_check(self):
        """Check API health and get metrics"""
        async with self.session.get(f"{self.base_url}/health") as response:
            return await response.json()
    
    async def get_metrics(self):
        """Get service performance metrics"""
        async with self.session.get(f"{self.base_url}/metrics") as response:
            return await response.json()
    
    async def prepare_avatar(self, video_path: str, bbox_shift: int = 0) -> str:
        """Prepare avatar from video file"""
        with open(video_path, 'rb') as f:
            files = {'video': f}
            data = {'bbox_shift': bbox_shift}
            
            async with self.session.post(
                f"{self.base_url}/avatar/prepare",
                data=data,
                files=files
            ) as response:
                result = await response.json()
                return result["avatar_id"]
    
    async def process_audio_file(self, avatar_id: str, audio_path: str, **params) -> str:
        """Process complete audio file (traditional mode)"""
        with open(audio_path, 'rb') as f:
            files = {'audio': f}
            
            async with self.session.post(
                f"{self.base_url}/avatar/{avatar_id}/generate",
                data=params,
                files=files
            ) as response:
                result = await response.json()
                return result["task_id"]
    
    async def wait_for_completion(self, task_id: str, timeout: int = 300) -> dict:
        """Wait for task to complete with timeout"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            async with self.session.get(f"{self.base_url}/task/{task_id}/status") as response:
                status = await response.json()
                
                if status["status"] == "completed":
                    return status
                elif status["status"] == "failed":
                    raise Exception(f"Task failed: {status.get('error', 'Unknown error')}")
                
                await asyncio.sleep(2)
        
        raise TimeoutError(f"Task {task_id} did not complete within {timeout} seconds")
    
    async def process_audio_chunks(self, avatar_id: str, audio_chunks: List[bytes], **params) -> str:
        """Process audio in chunks (batch mode)"""
        # Convert audio chunks to base64
        chunk_data = []
        for i, chunk in enumerate(audio_chunks):
            chunk_data.append({
                "chunk_id": f"chunk_{i}",
                "audio_data": base64.b64encode(chunk).decode(),
                "sequence_number": i,
                "is_final": i == len(audio_chunks) - 1,
                "format": "wav",
                "sample_rate": 16000
            })
        
        request_data = {
            "avatar_id": avatar_id,
            "audio_chunks": chunk_data,
            "output_format": "mp4",
            **params
        }
        
        async with self.session.post(
            f"{self.base_url}/avatar/{avatar_id}/process/batch",
            json=request_data
        ) as response:
            result = await response.json()
            return result["task_id"]
    
    async def process_single_chunk(self, avatar_id: str, audio_chunk: bytes, chunk_id: str, sequence_number: int) -> dict:
        """Process a single audio chunk (microservice mode)"""
        chunk_data = {
            "chunk_id": chunk_id,
            "audio_data": base64.b64encode(audio_chunk).decode(),
            "sequence_number": sequence_number,
            "is_final": False,
            "format": "wav",
            "sample_rate": 16000
        }
        
        async with self.session.post(
            f"{self.base_url}/avatar/{avatar_id}/process/chunk",
            json=chunk_data
        ) as response:
            return await response.json()
    
    async def start_streaming_session(self, avatar_id: str, session_id: Optional[str] = None, **params) -> dict:
        """Start a WebSocket streaming session"""
        request_data = {
            "avatar_id": avatar_id,
            "session_id": session_id or f"session_{int(time.time())}",
            **params
        }
        
        async with self.session.post(
            f"{self.base_url}/avatar/{avatar_id}/stream/start",
            json=request_data
        ) as response:
            return await response.json()


# =============================================================================
# 📝 USAGE EXAMPLES
# =============================================================================

async def example_traditional_processing():
    """Example: Traditional full audio file processing"""
    print("🎬 Traditional Processing Example")
    
    async with MuseTalkClient() as client:
        # Check service health
        health = await client.health_check()
        print(f"Service status: {health['status']}")
        
        # Prepare avatar (assuming you have a video file)
        # avatar_id = await client.prepare_avatar("path/to/video.mp4")
        avatar_id = "existing_avatar_id"  # Use existing avatar
        
        # Process audio file
        task_id = await client.process_audio_file(
            avatar_id=avatar_id,
            audio_path="path/to/audio.wav",
            fps=25,
            batch_size=20
        )
        
        # Wait for completion
        result = await client.wait_for_completion(task_id)
        print(f"✅ Processing completed in {result['total_time_seconds']}s")
        print(f"📹 Output: {result['output_path']}")


async def example_chunked_processing():
    """Example: Process audio in chunks for streaming apps"""
    print("🎵 Chunked Processing Example")
    
    async with MuseTalkClient() as client:
        avatar_id = "existing_avatar_id"
        
        # Simulate audio chunks (in real app, these would come from audio stream)
        audio_chunks = [
            b"fake_audio_chunk_1",  # Replace with real audio data
            b"fake_audio_chunk_2",
            b"fake_audio_chunk_3"
        ]
        
        # Process in batch mode
        task_id = await client.process_audio_chunks(
            avatar_id=avatar_id,
            audio_chunks=audio_chunks,
            fps=25,
            batch_size=10
        )
        
        result = await client.wait_for_completion(task_id)
        print(f"✅ Processed {len(audio_chunks)} chunks")


async def example_microservice_integration():
    """Example: Single chunk processing for microservice architecture"""
    print("🔧 Microservice Integration Example")
    
    async with MuseTalkClient() as client:
        avatar_id = "existing_avatar_id"
        
        # Process individual chunks (ideal for real-time systems)
        for i in range(3):
            chunk = b"fake_audio_data"  # Replace with real audio
            
            result = await client.process_single_chunk(
                avatar_id=avatar_id,
                audio_chunk=chunk,
                chunk_id=f"chunk_{i}",
                sequence_number=i
            )
            
            print(f"📦 Chunk {i}: {result['processing_time_ms']}ms")


async def example_streaming_websocket():
    """Example: Real-time WebSocket streaming"""
    print("🌊 WebSocket Streaming Example")
    
    async with MuseTalkClient() as client:
        avatar_id = "existing_avatar_id"
        
        # Start streaming session
        session = await client.start_streaming_session(
            avatar_id=avatar_id,
            fps=25,
            batch_size=5  # Smaller batches for real-time
        )
        
        print(f"🚀 Session started: {session['session_id']}")
        print(f"🔌 WebSocket URL: {session['websocket_url']}")
        
        # Connect to WebSocket (simplified example)
        # In real app, you'd stream audio and receive video frames
        # websocket_url = session['websocket_url']
        # async with websockets.connect(websocket_url) as websocket:
        #     # Send audio chunks and receive frames
        #     pass


async def example_service_monitoring():
    """Example: Monitor service performance"""
    print("📊 Service Monitoring Example")
    
    async with MuseTalkClient() as client:
        # Get health status
        health = await client.health_check()
        print(f"🏥 Health: {health['status']}")
        print(f"💾 GPU Memory: {health.get('gpu_memory_used', 'N/A')}GB / {health.get('gpu_memory_total', 'N/A')}GB")
        print(f"📈 Active Tasks: {health['active_tasks']}")
        
        # Get performance metrics
        metrics = await client.get_metrics()
        print(f"⚡ Average Processing: {metrics['average_processing_time']:.1f}s")
        print(f"🎯 Throughput: {metrics['throughput_fps']:.1f} fps")
        print(f"❌ Error Rate: {metrics['error_rate']:.2%}")


# =============================================================================
# 🚀 RUN EXAMPLES
# =============================================================================

async def main():
    """Run all examples"""
    print("🎭 MuseTalk API Client Examples\n")
    
    try:
        await example_service_monitoring()
        print("\n" + "="*50 + "\n")
        
        # await example_traditional_processing()
        # print("\n" + "="*50 + "\n")
        
        # await example_chunked_processing()
        # print("\n" + "="*50 + "\n")
        
        # await example_microservice_integration()
        # print("\n" + "="*50 + "\n")
        
        # await example_streaming_websocket()
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())