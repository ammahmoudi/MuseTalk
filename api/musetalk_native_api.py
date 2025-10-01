"""
🚀 MuseTalk Native API - Using MuseTalk's Original Scripts
Real-time lip-sync avatar generation using MuseTalk's native inference pipeline
"""
import sys
import uuid
import subprocess
import asyncio
import shutil
import yaml
import json
from pathlib import Path
from typing import Optional, Dict, List
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn

# Add MuseTalk to path
musetalk_root = Path(__file__).parent.parent
sys.path.append(str(musetalk_root))

# Global model variables (loaded once like realtime script)
global_models = {
    "vae": None,
    "unet": None, 
    "pe": None,
    "whisper": None,
    "audio_processor": None,
    "timesteps": None,
    "device": None,
    "weight_dtype": None,
    "fp": None
}

# Pydantic models
class AvatarResponse(BaseModel):
    avatar_id: str
    status: str
    message: str
    preprocessing_time: Optional[float] = None

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
    parameters: Optional[Dict] = None

# FastAPI app
app = FastAPI(
    title="MuseTalk Native API",
    description="Real-time lip-sync using MuseTalk's original scripts and workflow",
    version="2.0.0"
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
    """Load persistent data and models on startup"""
    print("🚀 Starting MuseTalk Native API...")
    print(f"📂 MuseTalk Root: {musetalk_root}")
    print(f"📁 Models Directory: {MODELS_DIR}")
    print(f"💾 Temp Directory: {TEMP_DIR}")
    print(f"📊 Data Directory: {DATA_DIR}")
    
    # Load persistent data
    load_avatars_data()
    load_tasks_data()
    
    # Load models globally (like realtime script)
    await load_global_models()

async def load_global_models():
    """Load models once at startup exactly like realtime script"""
    def _load_models():
        import torch
        from musetalk.utils.utils import load_all_model
        from musetalk.utils.audio_processor import AudioProcessor
        from musetalk.utils.face_parsing import FaceParsing
        from transformers import WhisperModel
        
        print("🤖 Loading MuseTalk models globally...")
        
        # Set device exactly like realtime script
        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        print(f"📱 Using device: {device}")
        
        # Load models exactly like realtime script
        vae, unet, pe = load_all_model(
            unet_model_path=str(MODELS_DIR / "musetalkV15" / "unet.pth"),
            vae_type="sd-vae",
            unet_config=str(MODELS_DIR / "musetalkV15" / "musetalk.json"),
            device=device
        )
        
        # Apply half precision exactly like working script
        timesteps = torch.tensor([0], device=device)
        pe = pe.half().to(device)
        vae.vae = vae.vae.half().to(device)
        unet.model = unet.model.half().to(device)
        
        # Initialize audio processor and Whisper (like script)
        audio_processor = AudioProcessor(feature_extractor_path=str(MODELS_DIR / "whisper"))
        weight_dtype = unet.model.dtype
        whisper = WhisperModel.from_pretrained(str(MODELS_DIR / "whisper"))
        whisper = whisper.to(device=device, dtype=weight_dtype).eval()
        whisper.requires_grad_(False)
        
        # Initialize face parser with V15 settings
        fp = FaceParsing(left_cheek_width=90, right_cheek_width=90)
        
        print("✅ Global models loaded successfully!")
        
        return {
            "vae": vae,
            "unet": unet,
            "pe": pe,
            "whisper": whisper,
            "audio_processor": audio_processor,
            "timesteps": timesteps,
            "device": device,
            "weight_dtype": weight_dtype,
            "fp": fp
        }
    
    # Load models in executor to avoid blocking startup
    loaded_models = await asyncio.get_event_loop().run_in_executor(
        executor, _load_models
    )
    
    # Store in global variables
    global_models.update(loaded_models)

# Global storage for tasks and avatars
tasks: Dict[str, Dict] = {}
avatars: Dict[str, Dict] = {}
executor = ThreadPoolExecutor(max_workers=2)

# Paths
TEMP_DIR = musetalk_root / "temp"
AVATARS_DIR = TEMP_DIR / "avatars"
RESULTS_DIR = musetalk_root / "results"
MODELS_DIR = musetalk_root / "models"
DATA_DIR = musetalk_root / "data" / "api_storage"

# Persistence files
TASKS_FILE = DATA_DIR / "tasks.json"
AVATARS_FILE = DATA_DIR / "avatars.json"

# Ensure directories exist
TEMP_DIR.mkdir(exist_ok=True)
AVATARS_DIR.mkdir(exist_ok=True)
RESULTS_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

def save_tasks_data():
    """Save tasks data to persistent storage"""
    try:
        with open(TASKS_FILE, 'w') as f:
            json.dump(tasks, f, indent=2, default=str)
        print(f"💾 Tasks data saved to {TASKS_FILE}")
    except Exception as e:
        print(f"⚠️ Failed to save tasks data: {e}")

def save_avatars_data():
    """Save avatars data to persistent storage"""
    try:
        with open(AVATARS_FILE, 'w') as f:
            json.dump(avatars, f, indent=2, default=str)
        print(f"💾 Avatars data saved to {AVATARS_FILE}")
    except Exception as e:
        print(f"⚠️ Failed to save avatars data: {e}")

def load_tasks_data():
    """Load tasks data from persistent storage"""
    global tasks
    try:
        if TASKS_FILE.exists():
            with open(TASKS_FILE, 'r') as f:
                tasks = json.load(f)
            print(f"📂 Loaded {len(tasks)} tasks from {TASKS_FILE}")
        else:
            print("📂 No existing tasks file found, starting with empty tasks")
    except Exception as e:
        print(f"⚠️ Failed to load tasks data: {e}")
        tasks = {}

def load_avatars_data():
    """Load avatars data from persistent storage"""
    global avatars
    try:
        if AVATARS_FILE.exists():
            with open(AVATARS_FILE, 'r') as f:
                avatars = json.load(f)
            print(f"🎭 Loaded {len(avatars)} avatars from {AVATARS_FILE}")
            
            # Validate that avatar directories still exist
            valid_avatars = {}
            for avatar_id, avatar_data in avatars.items():
                avatar_dir = Path(avatar_data.get("avatar_dir", ""))
                if avatar_dir.exists():
                    valid_avatars[avatar_id] = avatar_data
                else:
                    print(f"⚠️ Avatar {avatar_id} directory not found, removing from list")
            
            avatars = valid_avatars
            if len(valid_avatars) != len(avatars):
                save_avatars_data()  # Save cleaned up data
                
        else:
            print("🎭 No existing avatars file found, starting with empty avatars")
    except Exception as e:
        print(f"⚠️ Failed to load avatars data: {e}")
        avatars = {}

def run_musetalk_command(cmd: List[str], cwd: Path = None) -> subprocess.CompletedProcess:
    """Run a MuseTalk command and return the result"""
    if cwd is None:
        cwd = musetalk_root
    
    print(f"🔧 Running command: {' '.join(cmd)}")
    print(f"📂 Working directory: {cwd}")
    
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            shell=True if sys.platform == 'win32' else False
        )
        
        if result.stdout:
            print(f"✅ Command output: {result.stdout}")
        if result.stderr:
            print(f"⚠️ Command stderr: {result.stderr}")
            
        return result
    except Exception as e:
        print(f"💥 Command failed: {e}")
        raise

def create_inference_config(avatar_id: str, video_path: str, audio_path: str, 
                          bbox_shift: int = 0, result_name: str = None) -> Path:
    """Create MuseTalk inference config file"""
    config_dir = TEMP_DIR / "configs"
    config_dir.mkdir(exist_ok=True)
    
    config_data = {
        f"{avatar_id}": {
            "video_path": str(video_path),
            "audio_path": str(audio_path),
            "bbox_shift": bbox_shift
        }
    }
    
    if result_name:
        config_data[avatar_id]["result_name"] = result_name
    
    config_path = config_dir / f"{avatar_id}_inference.yaml"
    with open(config_path, 'w') as f:
        yaml.dump(config_data, f)
    
    return config_path

@app.get("/")
async def root():
    """API health check with system info"""
    import torch
    
    cuda_available = torch.cuda.is_available()
    device_info = {
        "cuda_available": cuda_available,
        "device_count": torch.cuda.device_count() if cuda_available else 0
    }
    
    if cuda_available:
        device_info.update({
            "current_device": torch.cuda.current_device(),
            "device_name": torch.cuda.get_device_name(0),
            "memory_total": f"{torch.cuda.get_device_properties(0).total_memory // (1024**3)}GB"
        })
    
    # Check MuseTalk models
    models_status = {
        "models_dir_exists": MODELS_DIR.exists(),
        "unet_v15_exists": (MODELS_DIR / "musetalkV15" / "unet.pth").exists(),
        "whisper_exists": (MODELS_DIR / "whisper").exists(),
    }
    
    return {
        "status": "healthy",
        "message": "🚀 MuseTalk Native API is running!",
        "device_info": device_info,
        "models_status": models_status,
        "active_avatars": len(avatars),
        "active_tasks": len(tasks)
    }

@app.post("/avatar/prepare", response_model=AvatarResponse)
async def prepare_avatar(
    background_tasks: BackgroundTasks,
    video: UploadFile = File(..., description="Avatar video file"),
    bbox_shift: int = Form(0, ge=-20, le=20, description="Bounding box shift")
):
    """
    Prepare avatar video for inference (NOT training preprocessing)
    This extracts frames and landmarks for real-time lip-sync generation
    Uses the same approach as app.py and scripts/inference.py
    """
    avatar_id = str(uuid.uuid4())
    
    # Validate file
    if not video.filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
        raise HTTPException(status_code=400, detail="Invalid video format")
    
    # Create avatar directory
    avatar_dir = AVATARS_DIR / avatar_id
    avatar_dir.mkdir(parents=True, exist_ok=True)
    
    # Save uploaded video
    video_path = avatar_dir / f"input_video{Path(video.filename).suffix}"
    with open(video_path, "wb") as f:
        shutil.copyfileobj(video.file, f)
    
    # Store avatar info
    avatars[avatar_id] = {
        "status": "preprocessing",
        "video_path": str(video_path),
        "bbox_shift": bbox_shift,
        "avatar_dir": str(avatar_dir),
        "created_at": str(asyncio.get_event_loop().time())
    }
    
    # Save avatars data persistently
    save_avatars_data()
    
    # Start preprocessing in background
    background_tasks.add_task(run_preprocessing, avatar_id)
    
    return AvatarResponse(
        avatar_id=avatar_id,
        status="preparing", 
        message="Avatar preparation started for inference (frame extraction + landmark detection)"
    )

async def run_preprocessing(avatar_id: str):
    """Prepare avatar for inference using the same approach as app.py and scripts/inference.py"""
    try:
        from musetalk.utils.preprocessing import get_landmark_and_bbox
        from musetalk.utils.utils import get_video_fps, get_file_type
        import pickle
        import glob
        
        avatar_data = avatars[avatar_id]
        video_path = avatar_data["video_path"]
        bbox_shift = avatar_data["bbox_shift"]
        avatar_dir = Path(avatar_data["avatar_dir"])
        
        print(f"🎬 Preparing avatar {avatar_id} for inference (not training preprocessing)")
        avatars[avatar_id]["status"] = "processing"
        
        # Create frames directory
        frames_dir = avatar_dir / "frames"
        frames_dir.mkdir(exist_ok=True)
        
        # Extract frames using OpenCV (same as realtime_inference.py)
        if get_file_type(video_path) == "video":
            print("📸 Extracting video frames using OpenCV...")
            
            def extract_frames():
                import cv2
                cap = cv2.VideoCapture(video_path)
                count = 0
                while True:
                    ret, frame = cap.read()
                    if ret:
                        cv2.imwrite(f"{frames_dir}/{count:08d}.png", frame)
                        count += 1
                    else:
                        break
                cap.release()
                return count
            
            frame_count = await asyncio.get_event_loop().run_in_executor(executor, extract_frames)
            input_img_list = sorted(glob.glob(str(frames_dir / "*.[jpJP][pnPN]*[gG]")))
            fps = get_video_fps(video_path)
        elif get_file_type(video_path) == "image":
            input_img_list = [video_path]
            fps = 25
        else:
            raise ValueError(f"Unsupported video format: {video_path}")
        
        if not input_img_list:
            raise Exception("No frames extracted from video")
            
        print(f"📊 Extracted {frame_count} frames ({len(input_img_list)} files found)")
        
        # Process landmarks using the same function as app.py
        print("🔍 Processing landmarks and bounding boxes...")
        
        def process_landmarks():
            coord_list, frame_list = get_landmark_and_bbox(input_img_list, bbox_shift)
            return coord_list, frame_list
        
        coord_list, frame_list = await asyncio.get_event_loop().run_in_executor(
            executor, process_landmarks
        )
        
        # Save coordinates
        coord_file = avatar_dir / "coordinates.pkl"
        with open(coord_file, 'wb') as f:
            pickle.dump(coord_list, f)
        
        # Pre-compute latents and masks for real-time mode (like realtime_inference.py)
        print("🚀 Pre-computing latents and masks for real-time inference...")
        
        def compute_realtime_materials():
            from musetalk.utils.blending import get_image_prepare_material
            import cv2
            
            # Use global models (no need to load again!)
            vae = global_models["vae"]
            fp = global_models["fp"]
            
            input_latent_list = []
            mask_list = []
            mask_coords_list = []
            
            coord_placeholder = (0.0, 0.0, 0.0, 0.0)
            for i, (bbox, frame) in enumerate(zip(coord_list, frame_list)):
                if bbox == coord_placeholder:
                    continue
                    
                x1, y1, x2, y2 = bbox
                # Add extra margin for v15 exactly like realtime script
                extra_margin = 10
                y2 = y2 + extra_margin
                y2 = min(y2, frame.shape[0])
                coord_list[i] = [x1, y1, x2, y2]  # Update coord_list like script does
                
                # Crop and resize frame
                crop_frame = frame[y1:y2, x1:x2]
                resized_crop_frame = cv2.resize(crop_frame, (256, 256), interpolation=cv2.INTER_LANCZOS4)
                
                # Get latents for UNet
                latents = vae.get_latents_for_unet(resized_crop_frame)
                input_latent_list.append(latents)
                
                # Prepare mask and crop box
                mask, crop_box = get_image_prepare_material(frame, [x1, y1, x2, y2], fp=fp, mode="jaw")
                mask_list.append(mask)
                mask_coords_list.append(crop_box)
            
            # Create cycle lists (forward + reverse for smooth looping)
            frame_list_cycle = frame_list + frame_list[::-1]
            coord_list_cycle = coord_list + coord_list[::-1] 
            input_latent_list_cycle = input_latent_list + input_latent_list[::-1]
            mask_list_cycle = mask_list + mask_list[::-1]
            mask_coords_list_cycle = mask_coords_list + mask_coords_list[::-1]
            
            return {
                "latents": input_latent_list_cycle,
                "masks": mask_list_cycle, 
                "mask_coords": mask_coords_list_cycle,
                "frames": frame_list_cycle,
                "coords": coord_list_cycle
            }
        
        try:
            realtime_materials = await asyncio.get_event_loop().run_in_executor(
                executor, compute_realtime_materials
            )
            
            # Save all materials for real-time inference
            materials_dir = avatar_dir / "realtime_materials"
            materials_dir.mkdir(exist_ok=True)
            
            import torch
            torch.save(realtime_materials["latents"], materials_dir / "latents.pt")
            
            with open(materials_dir / "masks.pkl", 'wb') as f:
                pickle.dump(realtime_materials["masks"], f)
            with open(materials_dir / "mask_coords.pkl", 'wb') as f:
                pickle.dump(realtime_materials["mask_coords"], f)
            with open(materials_dir / "frames.pkl", 'wb') as f:
                pickle.dump(realtime_materials["frames"], f)
            with open(materials_dir / "coords.pkl", 'wb') as f:
                pickle.dump(realtime_materials["coords"], f)
                
            print("✅ Real-time materials pre-computed and saved")
            
        except Exception as e:
            print(f"⚠️ Failed to pre-compute real-time materials: {e}")
            # Continue without real-time materials
        
        # Save preprocessing info
        preprocess_info = {
            "video_path": video_path,
            "bbox_shift": bbox_shift,
            "fps": fps,
            "frame_count": len(coord_list),
            "frames_dir": str(frames_dir),
            "coord_file": str(coord_file),
            "realtime_ready": True,
            "materials_dir": str(materials_dir) if 'materials_dir' in locals() else None
        }
        
        info_file = avatar_dir / "preprocess_info.json"
        with open(info_file, 'w') as f:
            json.dump(preprocess_info, f, indent=2)
        
        # Mark as ready
        avatars[avatar_id]["status"] = "ready"
        avatars[avatar_id]["preprocessed"] = True
        avatars[avatar_id]["fps"] = fps
        avatars[avatar_id]["frame_count"] = len(coord_list)
        
        # Save avatars data persistently
        save_avatars_data()
        
        print(f"✅ Avatar preparation completed for {avatar_id} - {len(coord_list)} frames ready for inference")
        
    except Exception as e:
        avatars[avatar_id]["status"] = "failed"
        avatars[avatar_id]["error"] = str(e)
        
        # Save avatars data persistently
        save_avatars_data()
        print(f"💥 Preprocessing exception for avatar {avatar_id}: {e}")

@app.post("/avatar/{avatar_id}/generate", response_model=GenerationResponse)
async def generate_video(
    avatar_id: str,
    background_tasks: BackgroundTasks,
    audio: UploadFile = File(..., description="Audio file for lip-sync"),
    use_realtime: bool = Form(True, description="Use real-time inference mode (recommended)"),
    fps: int = Form(25, ge=10, le=60, description="Output video FPS"),
    batch_size: int = Form(20, ge=1, le=32, description="Inference batch size (20 works best)"),
    bbox_shift: int = Form(0, ge=-50, le=50, description="Bounding box shift for face adjustment"),
    extra_margin: int = Form(10, ge=0, le=50, description="Extra margin for face cropping"),
    audio_padding_length_left: int = Form(2, ge=0, le=10, description="Left padding length for audio"),
    audio_padding_length_right: int = Form(2, ge=0, le=10, description="Right padding length for audio"),
    parsing_mode: str = Form("jaw", regex="^(jaw|mouth|face)$", description="Face blending parsing mode"),
    left_cheek_width: int = Form(90, ge=50, le=150, description="Width of left cheek region"),
    right_cheek_width: int = Form(90, ge=50, le=150, description="Width of right cheek region"),
    skip_save_images: bool = Form(False, description="Skip saving intermediate images for faster processing")
):
    """
    Generate lip-synced video using MuseTalk's native inference
    
    **Real-time Mode**: Uses pre-computed latents and masks for faster processing
    **Standard Mode**: Uses MuseTalk's scripts/inference.py for high quality
    """
    # Check if avatar exists and is ready
    if avatar_id not in avatars:
        raise HTTPException(status_code=404, detail="Avatar not found")
    
    avatar_data = avatars[avatar_id]
    if avatar_data["status"] != "ready":
        raise HTTPException(status_code=400, detail=f"Avatar not ready (status: {avatar_data['status']})")
    
    # Validate audio file
    if not audio.filename.lower().endswith(('.wav', '.mp3', '.m4a')):
        raise HTTPException(status_code=400, detail="Invalid audio format")
    
    # Generate task ID
    task_id = str(uuid.uuid4())
    
    # Save audio file
    avatar_dir = Path(avatar_data["avatar_dir"])
    audio_path = avatar_dir / f"input_audio{Path(audio.filename).suffix}"
    with open(audio_path, "wb") as f:
        shutil.copyfileobj(audio.file, f)
    
    # Create task with all parameters and timing
    tasks[task_id] = {
        "task_id": task_id,
        "avatar_id": avatar_id,
        "status": "queued",
        "audio_path": str(audio_path),
        "use_realtime": use_realtime,
        "fps": fps,
        "batch_size": batch_size,
        "bbox_shift": bbox_shift,
        "extra_margin": extra_margin,
        "audio_padding_length_left": audio_padding_length_left,
        "audio_padding_length_right": audio_padding_length_right,
        "parsing_mode": parsing_mode,
        "left_cheek_width": left_cheek_width,
        "right_cheek_width": right_cheek_width,
        "skip_save_images": skip_save_images,
        "created_at": datetime.now().isoformat(),
        "started_at": None,
        "completed_at": None,
        "total_time_seconds": None,
        "error": None
    }
    
    # Save tasks data persistently
    save_tasks_data()
    
    # Start generation in background
    background_tasks.add_task(run_inference, task_id)
    
    return GenerationResponse(
        task_id=task_id,
        avatar_id=avatar_id,
        status="queued",
        message="Video generation started using MuseTalk native inference"
    )

async def run_inference(task_id: str):
    """Run MuseTalk inference using native approach with real-time support"""
    try:
        task_data = tasks[task_id]
        
        print(f"🎥 Starting {'real-time' if task_data['use_realtime'] else 'standard'} inference for task {task_id}")
        tasks[task_id]["status"] = "processing"
        tasks[task_id]["started_at"] = datetime.now().isoformat()
        save_tasks_data()
        
        start_time = datetime.now()
        
        if task_data["use_realtime"]:
            # Use real-time inference approach (like realtime_inference.py)
            await run_realtime_inference(task_id)
        else:
            # Use standard inference approach (like scripts/inference.py)
            await run_standard_inference(task_id)
            
        # Mark completion time and calculate duration
        end_time = datetime.now()
        total_seconds = (end_time - start_time).total_seconds()
        
        tasks[task_id]["status"] = "completed"
        tasks[task_id]["completed_at"] = end_time.isoformat()
        tasks[task_id]["total_time_seconds"] = total_seconds
        print(f"✅ Task {task_id} completed in {total_seconds:.2f} seconds")
        save_tasks_data()
            
    except Exception as e:
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["error"] = str(e)
        tasks[task_id]["completed_at"] = datetime.now().isoformat()
        if tasks[task_id]["started_at"]:
            start_time = datetime.fromisoformat(tasks[task_id]["started_at"])
            end_time = datetime.now()
            tasks[task_id]["total_time_seconds"] = (end_time - start_time).total_seconds()
        save_tasks_data()
        print(f"💥 Inference exception for task {task_id}: {e}")

async def run_realtime_inference(task_id: str):
    """Run real-time inference using pre-computed materials"""
    
    def _run_inference():
        """Heavy computation that runs in thread executor"""
        import torch
        import pickle
        
        task_data = tasks[task_id]
        avatar_data = avatars[task_data["avatar_id"]]
        
        # Load pre-computed materials
        avatar_dir = Path(avatar_data["avatar_dir"])
        materials_dir = avatar_dir / "realtime_materials"
        
        if not materials_dir.exists():
            raise Exception("Real-time materials not found. Avatar needs re-preparation.")
        
        # Load materials
        input_latent_list_cycle = torch.load(materials_dir / "latents.pt")
        
        with open(materials_dir / "masks.pkl", 'rb') as f:
            mask_list_cycle = pickle.load(f)
        with open(materials_dir / "mask_coords.pkl", 'rb') as f:
            mask_coords_list_cycle = pickle.load(f)
        with open(materials_dir / "frames.pkl", 'rb') as f:
            frame_list_cycle = pickle.load(f)
        with open(materials_dir / "coords.pkl", 'rb') as f:
            coord_list_cycle = pickle.load(f)
        
        # Use global models (already loaded and optimized!)
        device = global_models["device"]
        vae = global_models["vae"]
        unet = global_models["unet"]
        pe = global_models["pe"]
        timesteps = global_models["timesteps"]
        audio_processor = global_models["audio_processor"]
        weight_dtype = global_models["weight_dtype"]
        whisper = global_models["whisper"]
        
        # Process audio
        audio_path = task_data["audio_path"]
        fps = task_data["fps"]
        
        print("start inference")
        # Extract audio features (with timing like script)
        import time
        start_time = time.time()
        whisper_input_features, librosa_length = audio_processor.get_audio_feature(audio_path, weight_dtype=weight_dtype)
        whisper_chunks = audio_processor.get_whisper_chunk(
            whisper_input_features,
            device,
            weight_dtype, 
            whisper,
            librosa_length,
            fps=fps,
            audio_padding_length_left=2,
            audio_padding_length_right=2
        )
        print(f"processing audio:{audio_path} costs {(time.time() - start_time) * 1000}ms")
        
        # Log video info like script
        video_num = len(whisper_chunks)
        print(f"Video frames to process: {video_num}")
        
        # Mark inference start time
        inference_start_time = time.time()
        
        # Create output directory
        output_dir = avatar_dir / "output" / task_id
        output_dir.mkdir(parents=True, exist_ok=True)
        
        return (
            whisper_chunks, input_latent_list_cycle, mask_list_cycle, 
            mask_coords_list_cycle, frame_list_cycle, coord_list_cycle,
            output_dir, fps, audio_path, vae, unet, pe, timesteps, video_num, inference_start_time
        )
    
    # Run heavy initialization in executor
    result = await asyncio.get_event_loop().run_in_executor(
        executor, _run_inference
    )
    
    (whisper_chunks, input_latent_list_cycle, mask_list_cycle, 
     mask_coords_list_cycle, frame_list_cycle, coord_list_cycle,
     output_dir, fps, audio_path, vae, unet, pe, timesteps, video_num, inference_start_time) = result
    
    # Run inference computation in executor to avoid blocking
    def _run_inference_computation():
        """The main inference loop that runs in thread executor"""
        import torch
        import queue
        import threading
        import time
        from musetalk.utils.utils import datagen
        from musetalk.utils.blending import get_image_blending
        import cv2
        import numpy as np
        from tqdm import tqdm
        
        task_data = tasks[task_id]
        batch_size = task_data["batch_size"]
        
        # Real-time inference with threading (like realtime script)
        video_num = len(whisper_chunks)
        res_frame_queue = queue.Queue()
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Frame processing function (runs in separate thread)
        def process_frames():
            idx = 0
            while idx < video_num:
                try:
                    res_frame = res_frame_queue.get(block=True, timeout=1)
                except queue.Empty:
                    continue
                    
                # Get corresponding original frame and coordinates
                bbox = coord_list_cycle[idx % len(coord_list_cycle)]
                ori_frame = frame_list_cycle[idx % len(frame_list_cycle)].copy()
                mask = mask_list_cycle[idx % len(mask_list_cycle)]
                mask_crop_box = mask_coords_list_cycle[idx % len(mask_coords_list_cycle)]
                
                x1, y1, x2, y2 = bbox
                try:
                    res_frame = cv2.resize(res_frame.astype(np.uint8), (x2 - x1, y2 - y1))
                except Exception:
                    idx += 1
                    continue
                    
                # Blend result with original frame
                combine_frame = get_image_blending(ori_frame, res_frame, bbox, mask, mask_crop_box)
                cv2.imwrite(f"{output_dir}/{str(idx).zfill(8)}.png", combine_frame)
                idx += 1
        
        # Start frame processing thread
        process_thread = threading.Thread(target=process_frames)
        process_thread.start()
        
        # Run inference with memory optimization like realtime script
        gen = datagen(whisper_chunks, input_latent_list_cycle, batch_size)
        
        # Use torch.no_grad() for memory efficiency during inference
        with torch.no_grad():
            # Add progress tracking like script        
            for i, (whisper_batch, latent_batch) in enumerate(tqdm(gen, total=int(np.ceil(float(video_num) / batch_size)))):
                audio_feature_batch = pe(whisper_batch.to(device))
                latent_batch = latent_batch.to(device=device, dtype=unet.model.dtype)
                
                pred_latents = unet.model(latent_batch, timesteps, encoder_hidden_states=audio_feature_batch).sample
                pred_latents = pred_latents.to(device=device, dtype=vae.vae.dtype)
                recon = vae.decode_latents(pred_latents)
                
                for res_frame in recon:
                    res_frame_queue.put(res_frame)
                
                # Clear intermediate tensors to free GPU memory
                del audio_feature_batch, latent_batch, pred_latents, recon
                torch.cuda.empty_cache()
        
        # Wait for frame processing to complete
        process_thread.join()
        
        # Final memory cleanup
        torch.cuda.empty_cache()
        
        # Log completion time like script (start_time from inference start)
        print(f"Total process time of {video_num} frames including saving images = {time.time() - inference_start_time}s")
        
        return True
    
    # Run inference computation in executor
    await asyncio.get_event_loop().run_in_executor(
        executor, _run_inference_computation
    )
    
    # Create final video
    output_video = output_dir.parent / f"{task_id}.mp4"
    cmd_img2video = f"ffmpeg -y -v warning -r {fps} -f image2 -i {output_dir}/%08d.png -vcodec libx264 -vf format=yuv420p -crf 18 {output_dir}/temp.mp4"
    
    result = await asyncio.get_event_loop().run_in_executor(
        executor,
        lambda: subprocess.run(cmd_img2video, shell=True, capture_output=True, text=True)
    )
    
    if result.returncode == 0:
        # Combine with audio
        cmd_combine_audio = f"ffmpeg -y -v warning -i {audio_path} -i {output_dir}/temp.mp4 {output_video}"
        result = await asyncio.get_event_loop().run_in_executor(
            executor,
            lambda: subprocess.run(cmd_combine_audio, shell=True, capture_output=True, text=True)
        )
        
        if result.returncode == 0:
            tasks[task_id]["status"] = "completed"
            tasks[task_id]["output_path"] = str(output_video)
            save_tasks_data()
            print(f"✅ Real-time inference completed for task {task_id}")
            
            # Cleanup temp files
            import shutil
            shutil.rmtree(output_dir)
        else:
            tasks[task_id]["status"] = "failed"
            tasks[task_id]["error"] = f"Audio combine failed: {result.stderr}"
            save_tasks_data()
    else:
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["error"] = f"Video creation failed: {result.stderr}"
        save_tasks_data()

async def run_standard_inference(task_id: str):
    """Run standard inference using MuseTalk scripts"""
    task_data = tasks[task_id]
    avatar_id = task_data["avatar_id"]
    avatar_data = avatars[avatar_id]
    
    # Create inference config
    config_path = create_inference_config(
        avatar_id=avatar_id,
        video_path=avatar_data["video_path"],
        audio_path=task_data["audio_path"],
        bbox_shift=avatar_data["bbox_shift"],
        result_name=f"{task_id}.mp4"
    )
    
    # Build command
    cmd = [
        sys.executable, "-m", "scripts.inference",
        "--inference_config", str(config_path),
        "--result_dir", str(RESULTS_DIR),
        "--fps", str(task_data["fps"]),
        "--batch_size", str(task_data["batch_size"]),
        "--version", "v15"
    ]
    
    # Add model paths
    unet_path = MODELS_DIR / "musetalkV15" / "unet.pth"
    if unet_path.exists():
        cmd.extend(["--unet_model_path", str(unet_path)])
    
    whisper_dir = MODELS_DIR / "whisper"
    if whisper_dir.exists():
        cmd.extend(["--whisper_dir", str(whisper_dir)])
    
    # Run inference
    result = await asyncio.get_event_loop().run_in_executor(
        executor,
        lambda: run_musetalk_command(cmd, musetalk_root)
    )
    
    if result.returncode == 0:
        # Find output video
        output_path = RESULTS_DIR / "v15" / f"{task_id}.mp4"
        if output_path.exists():
            tasks[task_id]["status"] = "completed"
            tasks[task_id]["output_path"] = str(output_path)
            save_tasks_data()
            print(f"✅ Standard inference completed for task {task_id}")
        else:
            tasks[task_id]["status"] = "failed"
            tasks[task_id]["error"] = "Output video not found"
            save_tasks_data()
    else:
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["error"] = result.stderr
        save_tasks_data()
        print(f"💥 Standard inference failed for task {task_id}: {result.stderr}")

@app.get("/avatar/{avatar_id}/status")
async def get_avatar_status(avatar_id: str):
    """Get avatar preparation status"""
    if avatar_id not in avatars:
        raise HTTPException(status_code=404, detail="Avatar not found")
    
    return avatars[avatar_id]

@app.get("/task/{task_id}/status", response_model=TaskStatus)
async def get_task_status(task_id: str):
    """Get task generation status"""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task_data = tasks[task_id]
    
    # Extract parameters for the response
    parameters = {
        "use_realtime": task_data.get("use_realtime"),
        "fps": task_data.get("fps"),
        "batch_size": task_data.get("batch_size"),
        "bbox_shift": task_data.get("bbox_shift"),
        "extra_margin": task_data.get("extra_margin"),
        "audio_padding_length_left": task_data.get("audio_padding_length_left"),
        "audio_padding_length_right": task_data.get("audio_padding_length_right"),
        "parsing_mode": task_data.get("parsing_mode"),
        "left_cheek_width": task_data.get("left_cheek_width"),
        "right_cheek_width": task_data.get("right_cheek_width"),
        "skip_save_images": task_data.get("skip_save_images")
    }
    
    return TaskStatus(
        task_id=task_id,
        status=task_data["status"],
        output_path=task_data.get("output_path"),
        error=task_data.get("error"),
        created_at=task_data.get("created_at"),
        started_at=task_data.get("started_at"),
        completed_at=task_data.get("completed_at"),
        total_time_seconds=task_data.get("total_time_seconds"),
        parameters=parameters
    )

@app.get("/task/{task_id}/download")
async def download_result(task_id: str):
    """Download generated video"""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task_data = tasks[task_id]
    if task_data["status"] != "completed":
        raise HTTPException(status_code=400, detail="Task not completed")
    
    output_path = task_data.get("output_path")
    if not output_path or not Path(output_path).exists():
        raise HTTPException(status_code=404, detail="Output file not found")
    
    return FileResponse(
        output_path,
        media_type="video/mp4",
        filename=f"musetalk_result_{task_id}.mp4"
    )

@app.get("/avatars")
async def list_avatars():
    """List all avatars with their status"""
    return {
        "avatars": avatars,
        "count": len(avatars)
    }

@app.get("/tasks")
async def list_tasks():
    """List all tasks with their status"""
    return {
        "tasks": tasks,
        "count": len(tasks)
    }

@app.get("/health")
async def health_check():
    """API health check with persistent data info"""
    return {
        "status": "healthy",
        "message": "MuseTalk Native API is running",
        "data_storage": {
            "avatars_file": str(AVATARS_FILE),
            "tasks_file": str(TASKS_FILE),
            "avatars_loaded": len(avatars),
            "tasks_loaded": len(tasks)
        },
        "directories": {
            "temp_dir": str(TEMP_DIR),
            "models_dir": str(MODELS_DIR),
            "data_dir": str(DATA_DIR)
        }
    }

@app.delete("/task/{task_id}")
async def delete_task(task_id: str):
    """Delete a specific task"""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Remove from memory
    del tasks[task_id]
    
    # Save tasks data persistently
    save_tasks_data()
    
    return {"message": f"Task {task_id} deleted"}

@app.delete("/avatar/{avatar_id}")
async def delete_avatar(avatar_id: str):
    """Delete avatar and its files"""
    if avatar_id not in avatars:
        raise HTTPException(status_code=404, detail="Avatar not found")
    
    # Delete avatar directory
    avatar_dir = Path(avatars[avatar_id]["avatar_dir"])
    if avatar_dir.exists():
        shutil.rmtree(avatar_dir)
    
    # Remove from memory
    del avatars[avatar_id]
    
    # Save avatars data persistently
    save_avatars_data()
    
    return {"message": f"Avatar {avatar_id} deleted"}

@app.get("/tasks", response_model=List[TaskStatus])
async def list_all_tasks():
    """List all tasks with their status and timing information"""
    task_list = []
    for task_id, task_data in tasks.items():
        # Extract parameters for the response
        parameters = {
            "use_realtime": task_data.get("use_realtime"),
            "fps": task_data.get("fps"),
            "batch_size": task_data.get("batch_size"),
            "bbox_shift": task_data.get("bbox_shift"),
            "extra_margin": task_data.get("extra_margin"),
            "audio_padding_length_left": task_data.get("audio_padding_length_left"),
            "audio_padding_length_right": task_data.get("audio_padding_length_right"),
            "parsing_mode": task_data.get("parsing_mode"),
            "left_cheek_width": task_data.get("left_cheek_width"),
            "right_cheek_width": task_data.get("right_cheek_width"),
            "skip_save_images": task_data.get("skip_save_images")
        }
        
        task_list.append(TaskStatus(
            task_id=task_id,
            status=task_data["status"],
            output_path=task_data.get("output_path"),
            error=task_data.get("error"),
            created_at=task_data.get("created_at"),
            started_at=task_data.get("started_at"),
            completed_at=task_data.get("completed_at"),
            total_time_seconds=task_data.get("total_time_seconds"),
            parameters=parameters
        ))
    
    return task_list

if __name__ == "__main__":
    print("🚀 Starting MuseTalk Native API...")
    print(f"📂 MuseTalk Root: {musetalk_root}")
    print(f"📁 Models Directory: {MODELS_DIR}")
    print(f"💾 Temp Directory: {TEMP_DIR}")
    
    uvicorn.run(
        "musetalk_native_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )