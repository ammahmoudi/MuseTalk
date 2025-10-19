#!/usr/bin/env python3
"""
🚀 MuseTalk Mock API - For Development & Testing
Fast mock API with fake data for testing without real video processing
"""
import asyncio
import uuid
import time
import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import random

from fastapi import FastAPI, HTTPException, BackgroundTasks, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn

# Mock data models (same as real API)
class AvatarResponse(BaseModel):
    avatar_id: str
    status: str
    message: str
    preprocessing_time: Optional[float] = None
    steady_state_video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None

class GenerationResponse(BaseModel):
    task_id: str
    avatar_id: str
    status: str
    message: str
    output_path: Optional[str] = None

class TaskStatus(BaseModel):
    task_id: str
    status: str
    progress: Optional[float] = None
    output_path: Optional[str] = None
    error: Optional[str] = None
    created_at: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    total_time_seconds: Optional[float] = None

class AvatarInfo(BaseModel):
    avatar_id: str
    name: Optional[str] = None
    status: str
    created_at: str
    video_url: str
    steady_state_video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    frame_count: Optional[int] = None
    bbox_shift: int = 0

# Configuration
BASE_URL = os.getenv('MOCK_BASE_URL', os.getenv('BASE_URL', 'https://ai-icon.rastar.dev/mock'))  # Use production URL by default
TEST_ASSETS_DIR = Path(os.getenv('TEST_ASSETS_DIR', str(Path(__file__).parent.parent / "test_assets")))

print(f"🎭 Mock API Base URL: {BASE_URL}")
print(f"📁 Test Assets Directory: {TEST_ASSETS_DIR}")
print(f"📁 Test Assets Directory Exists: {TEST_ASSETS_DIR.exists()}")

# URL generation functions
def generate_download_url(task_id: str) -> str:
    return f"{BASE_URL.rstrip('/')}/task/{task_id}/download"

def generate_steady_state_url(avatar_id: str) -> str:
    return f"{BASE_URL.rstrip('/')}/avatar/{avatar_id}/steady-state"

def generate_thumbnail_url(avatar_id: str) -> str:
    return f"{BASE_URL.rstrip('/')}/avatar/{avatar_id}/thumbnail"

def generate_avatar_video_url(avatar_id: str) -> str:
    return f"{BASE_URL.rstrip('/')}/avatar/{avatar_id}/video"

# Mock data storage
mock_avatars: Dict[str, Dict] = {}
mock_tasks: Dict[str, Dict] = {}

# Initialize mock data with current avatars from temp directory
def initialize_mock_data():
    """Initialize mock avatars from existing temp directory"""
    temp_avatars_dir = Path("temp/avatars")
    
    if temp_avatars_dir.exists():
        for avatar_dir in temp_avatars_dir.iterdir():
            if avatar_dir.is_dir():
                avatar_id = avatar_dir.name
                
                # Get video file
                video_files = list(avatar_dir.glob("input_video.*"))
                video_path = str(video_files[0]) if video_files else None
                
                # Check for existing thumbnail
                thumbnail_files = list(avatar_dir.glob("thumbnail.*"))
                thumbnail_path = str(thumbnail_files[0]) if thumbnail_files else None
                
                # Check for steady state
                steady_state_files = list(avatar_dir.glob("steady_state.*"))
                steady_state_path = str(steady_state_files[0]) if steady_state_files else None
                
                mock_avatars[avatar_id] = {
                    "status": "ready",
                    "name": f"Test Avatar {avatar_id[:8]}",
                    "video_path": video_path,
                    "bbox_shift": 0,
                    "avatar_dir": str(avatar_dir),
                    "created_at": datetime.now().isoformat(),
                    "steady_state_video_path": steady_state_path,
                    "thumbnail_path": thumbnail_path,
                    "frame_count": random.randint(50, 300)
                }
                
    # Add some fake avatars if none exist
    if not mock_avatars:
        fake_avatars = [
            {"name": "John Doe", "frames": 124},
            {"name": "Jane Smith", "frames": 89}, 
            {"name": "Bob Wilson", "frames": 156},
            {"name": "Alice Johnson", "frames": 203}
        ]
        
        for fake_avatar in fake_avatars:
            avatar_id = str(uuid.uuid4())
            mock_avatars[avatar_id] = {
                "status": "ready",
                "name": fake_avatar["name"],
                "video_path": f"test_assets/avatars/avatar_{avatar_id[:8]}.mp4",
                "bbox_shift": 0,
                "avatar_dir": f"test_assets/avatars/{avatar_id}",
                "created_at": (datetime.now() - timedelta(hours=random.randint(1, 48))).isoformat(),
                "steady_state_video_path": f"test_assets/steady_state/steady_{avatar_id[:8]}.mp4",
                "thumbnail_path": f"test_assets/thumbnails/thumb_{avatar_id[:8]}.jpg",
                "frame_count": fake_avatar["frames"]
            }
    
    print(f"🎭 Initialized {len(mock_avatars)} mock avatars")

# Helper functions for audio/video processing
def find_test_video(avatar_id: str) -> Optional[str]:
    """Find a test video to use for mock results"""
    # Prioritize test_assets/videos folder for mock results
    test_video_dirs = [
        Path("test_assets/videos"),     # First priority: test videos
        Path("data/video"),            # Second: existing sample videos
        Path("test_assets/avatars")    # Last: avatar videos
    ]
    
    for video_dir in test_video_dirs:
        if video_dir.exists():
            video_files = list(video_dir.glob("*.mp4")) + list(video_dir.glob("*.avi")) + list(video_dir.glob("*.mov"))
            if video_files:
                selected_video = str(video_files[0])
                print(f"📹 Using test video: {selected_video}")
                return selected_video
    
    # Fallback to avatar's own video if available
    if avatar_id in mock_avatars:
        avatar_video = mock_avatars[avatar_id].get("video_path")
        if avatar_video and os.path.exists(avatar_video):
            print(f"📹 Using avatar video: {avatar_video}")
            return avatar_video
    
    print("⚠️ No test video found - place videos in test_assets/videos/")
    return None

async def get_audio_duration(audio_path: str) -> float:
    """Get audio duration in seconds using ffprobe"""
    try:
        cmd = [
            "ffprobe", "-v", "quiet", "-show_entries", "format=duration",
            "-of", "csv=p=0", audio_path
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0:
            duration = float(stdout.decode().strip())
            return duration
        else:
            print(f"⚠️ ffprobe failed: {stderr.decode()}")
            return 3.0  # Default fallback duration
            
    except Exception as e:
        print(f"⚠️ Error getting audio duration: {e}")
        return 3.0  # Default fallback duration

async def combine_audio_video(audio_path: str, video_path: str, output_path: str) -> bool:
    """Combine user audio with test video, adjusting video length to match audio duration"""
    try:
        # Get audio duration
        audio_duration = await get_audio_duration(audio_path)
        print(f"🎵 Audio duration: {audio_duration:.2f} seconds")
        
        # Create ffmpeg command to match video length to audio duration and replace audio
        cmd = [
            "ffmpeg", "-y",  # -y to overwrite output
            "-stream_loop", "-1",  # Loop video indefinitely
            "-i", video_path,      # Input video (looped)
            "-i", audio_path,      # Input audio
            "-t", str(audio_duration),  # Set output duration to audio length
            "-c:v", "libx264",     # Re-encode video to allow looping/trimming
            "-c:a", "aac",         # Audio codec
            "-map", "0:v",         # Map video from first input (video file)
            "-map", "1:a",         # Map audio from second input (user audio file)
            "-pix_fmt", "yuv420p", # Ensure compatibility
            "-r", "25",            # Set frame rate
            str(output_path)
        ]
        
        print(f"🎬 Running ffmpeg: adjusting video to {audio_duration:.2f}s")
        print(f"📹 Video source: {video_path}")
        print(f"🎵 Audio source: {audio_path}")
        print("🔄 Mapping: video from file + user audio")
        
        # Run ffmpeg command
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0:
            print(f"✅ Successfully combined audio and video: {output_path}")
            print(f"📹 Result video duration matches audio: {audio_duration:.2f}s")
            return True
        else:
            print(f"⚠️ ffmpeg failed (code {process.returncode}): {stderr.decode()}")
            # Try simpler approach without looping
            return await combine_audio_video_simple(audio_path, video_path, output_path, audio_duration)
            
    except FileNotFoundError:
        print("⚠️ ffmpeg not found - install ffmpeg for audio/video processing")
        return False
    except Exception as e:
        print(f"⚠️ Error combining audio/video: {e}")
        return False

async def combine_audio_video_simple(audio_path: str, video_path: str, output_path: str, audio_duration: float) -> bool:
    """Fallback: Simple combination without advanced looping"""
    try:
        cmd = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-i", audio_path,
            "-t", str(audio_duration),  # Trim to audio length
            "-c:v", "libx264",
            "-c:a", "aac",
            "-map", "0:v",         # Map video from first input
            "-map", "1:a",         # Map audio from second input (USER AUDIO)
            "-pix_fmt", "yuv420p",
            str(output_path)
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0:
            print(f"✅ Simple combine successful: {output_path}")
            return True
        else:
            print(f"⚠️ Simple combine failed: {stderr.decode()}")
            return False
            
    except Exception as e:
        print(f"⚠️ Simple combine error: {e}")
        return False

# FastAPI app
app = FastAPI(
    title="🎭 MuseTalk Mock API",
    description="""
    ## Mock API for Development & Testing
    
    **Features:**
    - 🚀 Instant responses (no real processing)
    - 🎬 Fake avatars and tasks
    - 📁 Uses test assets directory
    - 🔄 Simulates processing delays
    - 📊 Realistic status updates
    
    **Perfect for:**
    - Frontend development
    - API integration testing
    - Demo purposes
    - Development without GPU
    """,
    version="1.0.0-mock"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize mock data on startup"""
    initialize_mock_data()

@app.get("/")
async def root():
    """Mock health check"""
    return {
        "status": "healthy",
        "message": "🎭 MuseTalk Mock API is running!",
        "mode": "mock",
        "device": "mock-gpu",
        "avatars_count": len(mock_avatars),
        "tasks_count": len(mock_tasks),
        "test_assets_dir": str(TEST_ASSETS_DIR)
    }

@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint for monitoring"""
    try:
        import psutil
        system_available = True
    except ImportError:
        psutil = None
        system_available = False
    
    # Check if ffmpeg is available
    ffmpeg_available = False
    try:
        process = await asyncio.create_subprocess_exec(
            "ffmpeg", "-version",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await process.communicate()
        ffmpeg_available = process.returncode == 0
    except Exception:
        ffmpeg_available = False
    
    # Check test assets directory
    test_assets_exists = TEST_ASSETS_DIR.exists()
    test_videos_count = len(list(TEST_ASSETS_DIR.glob("videos/*.mp4"))) if test_assets_exists else 0
    
    health_data = {
        "status": "healthy",
        "timestamp": time.time(),
        "api_mode": "mock",
        "base_url": BASE_URL,
        "dependencies": {
            "ffmpeg_available": ffmpeg_available,
            "asyncio": True,
            "fastapi": True,
            "psutil_available": system_available
        },
        "test_assets": {
            "directory_exists": test_assets_exists,
            "test_videos_count": test_videos_count,
            "test_assets_path": str(TEST_ASSETS_DIR)
        },
        "mock_data": {
            "avatars_count": len(mock_avatars),
            "tasks_count": len(mock_tasks),
            "completed_tasks": len([t for t in mock_tasks.values() if t.get("status") == "completed"]),
            "processing_tasks": len([t for t in mock_tasks.values() if t.get("status") == "processing"]),
            "queued_tasks": len([t for t in mock_tasks.values() if t.get("status") == "queued"])
        },
        "endpoints": {
            "avatar_prepare": f"{BASE_URL}/avatar/prepare",
            "avatar_generate": f"{BASE_URL}/avatar/{{id}}/generate",
            "task_status": f"{BASE_URL}/task/{{id}}/status",
            "task_download": f"{BASE_URL}/task/{{id}}/download",
            "debug_avatars": f"{BASE_URL}/debug/avatars",
            "debug_tasks": f"{BASE_URL}/debug/tasks"
        }
    }
    
    # Add system info if psutil is available
    if system_available and psutil is not None:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        health_data["system"] = {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "memory_available_gb": round(memory.available / (1024**3), 2)
        }
    
    return health_data

@app.post("/avatar/prepare", response_model=AvatarResponse)
async def prepare_avatar(
    background_tasks: BackgroundTasks,
    video: UploadFile = File(..., description="Avatar video for preparation"),
    bbox_shift: int = Form(0, description="Bounding box shift")
):
    """Mock avatar preparation - instant fake processing"""
    
    avatar_id = str(uuid.uuid4())
    
    # Simulate file saving (but don't actually save)
    mock_avatars[avatar_id] = {
        "status": "preparing",
        "name": Path(video.filename).stem if video.filename else f"Avatar {avatar_id[:8]}",
        "video_path": f"test_assets/avatars/avatar_{avatar_id}.mp4",
        "bbox_shift": bbox_shift,
        "avatar_dir": f"test_assets/avatars/{avatar_id}",
        "created_at": datetime.now().isoformat(),
        "steady_state_video_path": f"test_assets/steady_state/steady_{avatar_id}.mp4",
        "thumbnail_path": f"test_assets/thumbnails/thumb_{avatar_id}.jpg",
        "frame_count": random.randint(50, 300)
    }
    
    # Simulate background processing
    background_tasks.add_task(mock_prepare_avatar, avatar_id)
    
    return AvatarResponse(
        avatar_id=avatar_id,
        status="preparing",
        message="🎭 Mock avatar preparation started! Will be ready in 2-3 seconds.",
        steady_state_video_url=generate_steady_state_url(avatar_id),
        thumbnail_url=generate_thumbnail_url(avatar_id)
    )

async def mock_prepare_avatar(avatar_id: str):
    """Simulate avatar preparation with realistic timing"""
    await asyncio.sleep(2)  # Simulate 2 seconds processing
    
    if avatar_id in mock_avatars:
        mock_avatars[avatar_id]["status"] = "ready"
        print(f"🎭 Mock avatar {avatar_id} preparation completed!")

@app.post("/avatar/{avatar_id}/generate", response_model=GenerationResponse)
async def generate_video(
    avatar_id: str,
    background_tasks: BackgroundTasks,
    audio: UploadFile = File(..., description="Audio file for lip-sync"),
    use_realtime: bool = Form(True),
    fps: int = Form(25),
    batch_size: int = Form(20)
):
    """Mock video generation - uses user audio with test videos for realistic results"""
    
    if avatar_id not in mock_avatars:
        raise HTTPException(status_code=404, detail="Avatar not found")
    
    if mock_avatars[avatar_id]["status"] != "ready":
        raise HTTPException(status_code=400, detail=f"Avatar not ready (status: {mock_avatars[avatar_id]['status']})")
    
    task_id = str(uuid.uuid4())
    
    # Save user audio for processing
    audio_content = await audio.read()
    audio_path = Path("test_assets") / "temp_audio" / f"audio_{task_id}.wav"
    audio_path.parent.mkdir(exist_ok=True)
    
    with open(audio_path, "wb") as f:
        f.write(audio_content)
    
    mock_tasks[task_id] = {
        "task_id": task_id,
        "avatar_id": avatar_id,
        "status": "queued",
        "audio_path": str(audio_path),
        "use_realtime": use_realtime,
        "fps": fps,
        "batch_size": batch_size,
        "created_at": datetime.now().isoformat(),
        "started_at": None,
        "completed_at": None,
        "total_time_seconds": None,
        "error": None,
        "output_path": None
    }
    
    # Start background processing with user audio
    background_tasks.add_task(mock_generate_video_with_audio, task_id)
    
    return GenerationResponse(
        task_id=task_id,
        avatar_id=avatar_id,
        status="queued",
        message="🎭 Mock video generation started! Using your audio with test video."
    )

async def mock_generate_video_with_audio(task_id: str):
    """Generate realistic mock video by combining user audio with test video"""
    if task_id not in mock_tasks:
        return
        
    # Mark as processing
    mock_tasks[task_id]["status"] = "processing"
    mock_tasks[task_id]["started_at"] = datetime.now().isoformat()
    
    try:
        # Get task info
        task = mock_tasks[task_id]
        avatar_id = task["avatar_id"]
        audio_path = task["audio_path"]
        
        # Find a test video to use
        test_video = find_test_video(avatar_id)
        
        if test_video and os.path.exists(audio_path):
            # Create output path
            output_dir = Path("test_assets") / "results"
            output_dir.mkdir(exist_ok=True)
            output_path = output_dir / f"result_{task_id}.mp4"
            
            # Combine user audio with test video using ffmpeg
            success = await combine_audio_video(audio_path, test_video, str(output_path))
            
            if success:
                mock_tasks[task_id]["output_path"] = str(output_path)
                print(f"🎭 Created realistic mock result: {output_path.name}")
            else:
                # Fallback to simple copy if ffmpeg fails
                import shutil
                shutil.copy(test_video, output_path)
                mock_tasks[task_id]["output_path"] = str(output_path)
                print(f"🎭 Used test video as fallback: {output_path.name}")
        else:
            # Create a simple mock result
            mock_tasks[task_id]["output_path"] = f"test_assets/results/mock_result_{task_id}.mp4"
            print("🎭 Created mock placeholder result")
        
        # Simulate realistic processing time
        processing_time = random.uniform(3.0, 5.0)
        await asyncio.sleep(processing_time)
        
        # Mark as completed with proper download URL
        end_time = datetime.now()
        mock_tasks[task_id]["status"] = "completed"
        mock_tasks[task_id]["completed_at"] = end_time.isoformat()
        mock_tasks[task_id]["total_time_seconds"] = processing_time
        mock_tasks[task_id]["download_url"] = generate_download_url(task_id)
        
        print(f"🎭 Mock task {task_id} completed in {processing_time:.1f}s")
        
    except Exception as e:
        # Handle errors gracefully
        mock_tasks[task_id]["status"] = "failed"
        mock_tasks[task_id]["error"] = str(e)
        print(f"❌ Mock task {task_id} failed: {e}")

@app.get("/avatar/{avatar_id}/status", response_model=AvatarInfo)
async def get_avatar_status(avatar_id: str):
    """Get mock avatar status"""
    if avatar_id not in mock_avatars:
        raise HTTPException(status_code=404, detail="Avatar not found")
    
    avatar_data = mock_avatars[avatar_id]
    
    return AvatarInfo(
        avatar_id=avatar_id,
        name=avatar_data.get("name", "Unknown"),
        status=avatar_data["status"],
        created_at=avatar_data.get("created_at", ""),
        video_url=generate_avatar_video_url(avatar_id),
        steady_state_video_url=generate_steady_state_url(avatar_id),
        thumbnail_url=generate_thumbnail_url(avatar_id),
        frame_count=avatar_data.get("frame_count"),
        bbox_shift=avatar_data.get("bbox_shift", 0)
    )

@app.get("/task/{task_id}/status", response_model=TaskStatus)
async def get_task_status(task_id: str):
    """Get mock task status"""
    if task_id not in mock_tasks:
        # Try to load from saved tasks file
        tasks_file = Path("data/api_storage/tasks.json")
        if tasks_file.exists():
            try:
                import json
                with open(tasks_file, 'r') as f:
                    saved_tasks = json.load(f)
                if task_id in saved_tasks:
                    task_data = saved_tasks[task_id]
                    # Fix URL format for old tasks
                    if task_data.get("output_path") and "localhost" in task_data.get("output_path", ""):
                        task_data["download_url"] = generate_download_url(task_id)
                    mock_tasks[task_id] = task_data  # Cache in memory
                else:
                    raise HTTPException(status_code=404, detail="Task not found")
            except (json.JSONDecodeError, FileNotFoundError):
                raise HTTPException(status_code=404, detail="Task not found")
        else:
            raise HTTPException(status_code=404, detail="Task not found")
    
    task_data = mock_tasks[task_id]
    
    return TaskStatus(
        task_id=task_id,
        status=task_data["status"],
        progress=1.0 if task_data["status"] == "completed" else 0.5 if task_data["status"] == "processing" else 0.0,
        output_path=task_data.get("download_url"),  # Use download_url instead of local path
        error=task_data.get("error"),
        created_at=task_data.get("created_at"),
        started_at=task_data.get("started_at"),
        completed_at=task_data.get("completed_at"),
        total_time_seconds=task_data.get("total_time_seconds")
    )

@app.get("/avatars")
async def list_avatars():
    """List all mock avatars"""
    avatar_list = []
    
    for avatar_id, avatar_data in mock_avatars.items():
        avatar_info = {
            "avatar_id": avatar_id,
            "name": avatar_data.get("name", "Unknown"),
            "status": avatar_data["status"],
            "created_at": avatar_data.get("created_at", ""),
            "video_url": generate_avatar_video_url(avatar_id),
            "steady_state_video_url": generate_steady_state_url(avatar_id),
            "thumbnail_url": generate_thumbnail_url(avatar_id),
            "frame_count": avatar_data.get("frame_count"),
            "bbox_shift": avatar_data.get("bbox_shift", 0),
            "has_steady_state": True,  # Always true in mock
            "has_thumbnail": True      # Always true in mock
        }
        avatar_list.append(avatar_info)
    
    return {
        "avatars": avatar_list,
        "count": len(avatar_list)
    }

@app.get("/tasks")
async def list_tasks():
    """List all mock tasks with proper URLs"""
    tasks_with_urls = {}
    
    for task_id, task_data in mock_tasks.items():
        task_copy = task_data.copy()
        # Ensure download_url is set for completed tasks
        if task_copy["status"] == "completed" and "download_url" not in task_copy:
            task_copy["download_url"] = generate_download_url(task_id)
        tasks_with_urls[task_id] = task_copy
    
    return {
        "tasks": tasks_with_urls,
        "count": len(tasks_with_urls)
    }

# File serving endpoints (serve test assets)
@app.get("/avatar/{avatar_id}/video")
async def get_avatar_video(avatar_id: str):
    """Serve mock avatar video"""
    if avatar_id not in mock_avatars:
        raise HTTPException(status_code=404, detail="Avatar not found")
    
    # First try to use avatar's own video if available
    avatar_data = mock_avatars[avatar_id]
    video_path = avatar_data.get("video_path")
    if video_path and Path(video_path).exists():
        return FileResponse(video_path, media_type="video/mp4")
    
    # Fallback to any video in test_assets/videos
    videos_dir = TEST_ASSETS_DIR / "videos"
    if videos_dir.exists():
        video_files = list(videos_dir.glob("*.mp4")) + list(videos_dir.glob("*.avi")) + list(videos_dir.glob("*.mov"))
        if video_files:
            print(f"📹 Using fallback avatar video: {video_files[0].name}")
            return FileResponse(video_files[0], media_type="video/mp4")
    
    raise HTTPException(status_code=404, detail="No avatar video found - place any video file in test_assets/videos/ or check avatar data")

@app.get("/avatar/{avatar_id}/steady-state")
async def get_steady_state_video(avatar_id: str):
    """Serve mock steady state video"""
    if avatar_id not in mock_avatars:
        raise HTTPException(status_code=404, detail="Avatar not found")
    
    print(f"🔍 Looking for steady state video for avatar: {avatar_id}")
    print(f"📁 TEST_ASSETS_DIR: {TEST_ASSETS_DIR}")
    
    # Look for any video file in steady_state directory
    steady_state_dir = TEST_ASSETS_DIR / "steady_state"
    print(f"📂 Steady state dir: {steady_state_dir}")
    print(f"📂 Steady state dir exists: {steady_state_dir.exists()}")
    
    if steady_state_dir.exists():
        # Find any video file
        video_files = list(steady_state_dir.glob("*.mp4")) + list(steady_state_dir.glob("*.avi")) + list(steady_state_dir.glob("*.mov"))
        print(f"🎬 Found steady state videos: {[f.name for f in video_files]}")
        if video_files:
            selected_video = video_files[0]
            print(f"✅ Serving steady state video: {selected_video}")
            return FileResponse(selected_video, media_type="video/mp4")
    
    # Fallback to any video from test_assets/videos
    videos_dir = TEST_ASSETS_DIR / "videos"
    print(f"📂 Videos fallback dir: {videos_dir}")
    print(f"📂 Videos dir exists: {videos_dir.exists()}")
    
    if videos_dir.exists():
        video_files = list(videos_dir.glob("*.mp4")) + list(videos_dir.glob("*.avi")) + list(videos_dir.glob("*.mov"))
        print(f"🎬 Found fallback videos: {[f.name for f in video_files]}")
        if video_files:
            selected_video = video_files[0]
            print(f"📹 Using fallback video for steady state: {selected_video.name}")
            return FileResponse(selected_video, media_type="video/mp4")
        
    raise HTTPException(status_code=404, detail="No steady state video found - place any video file in test_assets/steady_state/ or test_assets/videos/")

@app.get("/avatar/{avatar_id}/thumbnail")
async def get_thumbnail(avatar_id: str):
    """Serve mock thumbnail"""
    if avatar_id not in mock_avatars:
        raise HTTPException(status_code=404, detail="Avatar not found")
    
    # Look for any image file in thumbnails directory
    thumbnails_dir = TEST_ASSETS_DIR / "thumbnails"
    if thumbnails_dir.exists():
        # Find any image file
        image_files = list(thumbnails_dir.glob("*.jpg")) + list(thumbnails_dir.glob("*.jpeg")) + list(thumbnails_dir.glob("*.png"))
        if image_files:
            return FileResponse(image_files[0], media_type="image/jpeg")
    
    # Fallback: try to use avatar's own thumbnail if available
    if avatar_id in mock_avatars:
        avatar_data = mock_avatars[avatar_id]
        thumbnail_path = avatar_data.get("thumbnail_path")
        if thumbnail_path and os.path.exists(thumbnail_path):
            print(f"🖼️ Using avatar's own thumbnail: {thumbnail_path}")
            return FileResponse(thumbnail_path, media_type="image/jpeg")
        
    raise HTTPException(status_code=404, detail="No thumbnail found - place any image file (.jpg, .png) in test_assets/thumbnails/")

@app.get("/task/{task_id}/download")
async def download_result(task_id: str):
    """Serve mock generated video with user audio"""
    if task_id not in mock_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task_data = mock_tasks[task_id]
    if task_data["status"] != "completed":
        raise HTTPException(status_code=400, detail="Task not completed")
    
    # Try to serve the generated result with user audio
    output_path = task_data.get("output_path")
    if output_path and os.path.exists(output_path):
        return FileResponse(output_path, media_type="video/mp4", 
                          filename=f"mock_result_{task_id[:8]}.mp4")
    
    # Fallback to test result video
    test_video = TEST_ASSETS_DIR / "videos" / "sample_result.mp4"
    if test_video.exists():
        return FileResponse(test_video, media_type="video/mp4")
        
    raise HTTPException(status_code=404, detail="Result video not found - either generated result or test video")

# Debug endpoints
@app.get("/debug/avatars")
async def debug_avatars():
    """Debug endpoint to see raw avatar data"""
    return {
        "mock_avatars": mock_avatars,
        "count": len(mock_avatars),
        "test_assets_dir": str(TEST_ASSETS_DIR),
        "base_url": BASE_URL
    }

@app.get("/debug/tasks")
async def debug_tasks():
    """Debug endpoint to see raw task data with URLs"""
    tasks_debug = {}
    for task_id, task_data in mock_tasks.items():
        task_copy = task_data.copy()
        task_copy["download_url"] = generate_download_url(task_id)
        tasks_debug[task_id] = task_copy
        
    return {
        "mock_tasks": tasks_debug,
        "count": len(tasks_debug),
        "base_url": BASE_URL
    }

@app.post("/debug/create-test-avatar")
async def create_test_avatar(name: str = "Test Avatar"):
    """Create a test avatar instantly"""
    avatar_id = str(uuid.uuid4())
    
    mock_avatars[avatar_id] = {
        "status": "ready",
        "name": name,
        "video_path": f"test_assets/avatars/avatar_{avatar_id}.mp4",
        "bbox_shift": 0,
        "avatar_dir": f"test_assets/avatars/{avatar_id}",
        "created_at": datetime.now().isoformat(),
        "steady_state_video_path": f"test_assets/steady_state/steady_{avatar_id}.mp4",
        "thumbnail_path": f"test_assets/thumbnails/thumb_{avatar_id}.jpg",
        "frame_count": random.randint(50, 300)
    }
    
    return {
        "message": f"Test avatar '{name}' created!",
        "avatar_id": avatar_id,
        "avatar_info": await get_avatar_status(avatar_id)
    }

if __name__ == "__main__":
    print("🎭 Starting MuseTalk Mock API...")
    print(f"📁 Place test videos in: {TEST_ASSETS_DIR}")
    print("🚀 API will be available at: http://localhost:8001")
    
    uvicorn.run(app, host="0.0.0.0", port=8001)