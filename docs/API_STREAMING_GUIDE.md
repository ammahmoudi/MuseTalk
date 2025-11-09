# 🚀 MuseTalk Streaming API

A production-ready REST API for MuseTalk with streaming support, perfect for integrating with other services and real-time applications.

## 🌟 Features

- **🎭 Traditional Processing**: Complete audio file processing
- **🎵 Streaming Support**: Real-time audio chunk processing  
- **🔧 Microservice Ready**: Single chunk processing for service integration
- **🌊 WebSocket Streaming**: Real-time bidirectional streaming
- **📊 Health Monitoring**: Service metrics and GPU monitoring
- **⚡ Memory Optimized**: Global model loading with GPU memory management
- **🎛️ Full Parameter Control**: All realtime script parameters exposed

## 📋 API Endpoints

### Core Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/avatar/prepare` | Prepare avatar from video |
| `POST` | `/avatar/{avatar_id}/generate` | Traditional full audio processing |
| `GET` | `/task/{task_id}/status` | Get task status with timing |
| `GET` | `/tasks` | List all tasks with parameters |

### Streaming Endpoints  
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/avatar/{avatar_id}/stream/start` | Start streaming session |
| `WS` | `/avatar/{avatar_id}/stream/{session_id}/ws` | WebSocket streaming |
| `POST` | `/avatar/{avatar_id}/process/batch` | Process multiple audio chunks |
| `POST` | `/avatar/{avatar_id}/process/chunk` | Process single audio chunk |

### Monitoring Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Service health with GPU metrics |
| `GET` | `/metrics` | Performance metrics and throughput |

## 🔧 Integration Examples

### 1. Traditional Processing (Complete Files)

```python
import aiohttp

async def process_complete_audio():
    async with aiohttp.ClientSession() as session:
        # Upload and process complete audio file
        with open('audio.wav', 'rb') as f:
            files = {'audio': f}
            data = {
                'fps': 25,
                'batch_size': 20,
                'bbox_shift': 0
            }
            
            async with session.post(
                'http://localhost:8000/avatar/avatar_id/generate',
                data=data,
                files=files
            ) as response:
                result = await response.json()
                task_id = result['task_id']
        
        # Wait for completion
        while True:
            async with session.get(f'http://localhost:8000/task/{task_id}/status') as response:
                status = await response.json()
                if status['status'] == 'completed':
                    print(f"✅ Video ready: {status['output_path']}")
                    break
                await asyncio.sleep(2)
```

### 2. Streaming Integration (Audio Chunks)

```python
import base64

async def process_audio_stream():
    # Split audio into chunks (your audio streaming logic)
    audio_chunks = split_audio_into_chunks(audio_data)
    
    # Convert to API format
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
    
    # Process batch
    async with aiohttp.ClientSession() as session:
        request_data = {
            "avatar_id": "your_avatar_id",
            "audio_chunks": chunk_data,
            "output_format": "mp4",
            "fps": 25,
            "batch_size": 10
        }
        
        async with session.post(
            'http://localhost:8000/avatar/avatar_id/process/batch',
            json=request_data
        ) as response:
            result = await response.json()
            return result['task_id']
```

### 3. Microservice Integration (Single Chunks)

```python
async def process_single_audio_chunk(audio_chunk: bytes):
    """Perfect for microservice architectures"""
    
    chunk_data = {
        "chunk_id": f"chunk_{uuid.uuid4()}",
        "audio_data": base64.b64encode(audio_chunk).decode(),
        "sequence_number": 1,
        "format": "wav",
        "sample_rate": 16000
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            'http://localhost:8000/avatar/avatar_id/process/chunk',
            json=chunk_data
        ) as response:
            result = await response.json()
            # Get frame data immediately
            frame_data = result['frame_data']  # Base64 encoded frame
            return frame_data
```

### 4. WebSocket Real-time Streaming

```python
import websockets

async def realtime_streaming():
    # Start streaming session
    async with aiohttp.ClientSession() as session:
        request_data = {
            "avatar_id": "your_avatar_id", 
            "session_id": "session_123",
            "fps": 25,
            "batch_size": 5  # Smaller for real-time
        }
        
        async with session.post(
            'http://localhost:8000/avatar/avatar_id/stream/start',
            json=request_data
        ) as response:
            result = await response.json()
            websocket_url = result['websocket_url']
    
    # Connect to WebSocket
    async with websockets.connect(websocket_url) as websocket:
        # Send audio chunks, receive video frames
        for chunk in audio_stream:
            chunk_data = {
                "chunk_id": f"chunk_{time.time()}",
                "audio_data": base64.b64encode(chunk).decode(),
                "sequence_number": 1
            }
            
            await websocket.send(json.dumps(chunk_data))
            
            # Receive processed frame
            frame_response = await websocket.recv()
            frame_data = json.loads(frame_response)
            
            # Use frame_data['frame_data'] for display
            display_frame(frame_data['frame_data'])
```

## 📊 Monitoring and Health Checks

### Health Check
```python
async def check_service_health():
    async with aiohttp.ClientSession() as session:
        async with session.get('http://localhost:8000/health') as response:
            health = await response.json()
            
            print(f"Status: {health['status']}")
            print(f"GPU Memory: {health['gpu_memory_used']}GB / {health['gpu_memory_total']}GB")
            print(f"Active Tasks: {health['active_tasks']}")
            print(f"Uptime: {health['uptime_seconds']}s")
```

### Performance Metrics  
```python
async def get_performance_metrics():
    async with aiohttp.ClientSession() as session:
        async with session.get('http://localhost:8000/metrics') as response:
            metrics = await response.json()
            
            print(f"Tasks Processed: {metrics['total_tasks_processed']}")
            print(f"Average Time: {metrics['average_processing_time']:.1f}s")
            print(f"Throughput: {metrics['throughput_fps']:.1f} fps")
            print(f"Error Rate: {metrics['error_rate']:.2%}")
```

## 🎛️ Available Parameters

All parameters from the realtime script are supported:

```python
{
    "fps": 25,                           # Output video FPS
    "batch_size": 20,                    # Processing batch size
    "bbox_shift": 0,                     # Face bounding box adjustment  
    "extra_margin": 10,                  # Extra margin for face crop
    "audio_padding_length_left": 2,      # Audio padding (left)
    "audio_padding_length_right": 2,     # Audio padding (right)
    "parsing_mode": "jaw",               # Face parsing mode (jaw/full)
    "left_cheek_width": 90,              # Left cheek width
    "right_cheek_width": 90,             # Right cheek width  
    "skip_save_images": True             # Skip saving intermediate frames
}
```

## 🚀 Deployment

### Development
```bash
python api/musetalk_native_api.py
```

### Production
```bash
# Using Gunicorn with Uvicorn workers
gunicorn api.musetalk_native_api:app -w 1 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Using Docker (create Dockerfile)
docker build -t musetalk-api .
docker run -p 8000:8000 --gpus all musetalk-api
```

## 🏗️ Architecture Benefits

### For Real-time Applications
- **WebSocket streaming** for live video calls
- **Single chunk processing** for minimal latency
- **Memory optimized** for continuous operation

### For Microservices  
- **RESTful design** with standard HTTP codes
- **Health checks** for load balancer integration
- **Metrics endpoint** for monitoring systems
- **Stateless processing** for horizontal scaling

### For Batch Processing
- **Multi-chunk support** for longer audio files
- **Progress tracking** with detailed timing
- **Error handling** with comprehensive error messages

## 📈 Performance

Based on test results:
- **Average Processing Time**: ~87 seconds for 195 frames
- **Throughput**: ~2.2 FPS  
- **Memory Usage**: Optimized with global model loading
- **GPU Utilization**: Efficient with `torch.no_grad()` and memory cleanup

## 🔧 Integration Best Practices

1. **Use appropriate endpoint** for your use case:
   - Traditional: Complete files with `/generate` 
   - Streaming: Audio chunks with `/process/batch`
   - Real-time: Single chunks with `/process/chunk`
   - Live: WebSocket with `/stream`

2. **Monitor service health** before sending requests
3. **Implement retry logic** for failed requests  
4. **Use proper batch sizes** (20 for quality, 5-10 for real-time)
5. **Handle base64 encoding/decoding** for audio/video data

## 📚 Client Library

Use the provided `client_examples.py` for ready-to-use integration code with your applications.

## 🤝 Support

The API is now production-ready for integration with:
- Live streaming platforms
- Video conferencing systems  
- Content creation tools
- Batch processing pipelines
- Real-time communication apps