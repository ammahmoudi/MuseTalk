#!/usr/bin/env python3
"""
Download all required MuseTalk models using Python API
"""

import os
from pathlib import Path
from huggingface_hub import hf_hub_download, snapshot_download
import subprocess

# Set the checkpoints directory
checkpoints_dir = Path("models")

# Create necessary directories
dirs = [
    "models/musetalk",
    "models/musetalkV15", 
    "models/syncnet",
    "models/dwpose",
    "models/face-parse-bisent",
    "models/sd-vae",
    "models/whisper"
]

for d in dirs:
    Path(d).mkdir(parents=True, exist_ok=True)
    print(f"✓ Created directory: {d}")

print("\n📥 Downloading models...\n")

# Download MuseTalk V1.0 weights
print("⏳ Downloading MuseTalk V1.0...")
try:
    hf_hub_download(
        repo_id="TMElyralab/MuseTalk",
        filename="musetalk/musetalk.json",
        local_dir=str(checkpoints_dir)
    )
    hf_hub_download(
        repo_id="TMElyralab/MuseTalk",
        filename="musetalk/pytorch_model.bin",
        local_dir=str(checkpoints_dir)
    )
    print("✅ MuseTalk V1.0 downloaded\n")
except Exception as e:
    print(f"⚠️  MuseTalk V1.0 download failed: {e}\n")

# Download MuseTalk V1.5 weights
print("⏳ Downloading MuseTalk V1.5...")
try:
    hf_hub_download(
        repo_id="TMElyralab/MuseTalk",
        filename="musetalkV15/musetalk.json",
        local_dir=str(checkpoints_dir)
    )
    hf_hub_download(
        repo_id="TMElyralab/MuseTalk",
        filename="musetalkV15/unet.pth",
        local_dir=str(checkpoints_dir)
    )
    print("✅ MuseTalk V1.5 downloaded\n")
except Exception as e:
    print(f"⚠️  MuseTalk V1.5 download failed: {e}\n")

# Download SD VAE weights
print("⏳ Downloading SD VAE...")
try:
    snapshot_download(
        repo_id="stabilityai/sd-vae-ft-mse",
        local_dir=str(checkpoints_dir / "sd-vae"),
        allow_patterns=["config.json", "diffusion_pytorch_model.bin"]
    )
    print("✅ SD VAE downloaded\n")
except Exception as e:
    print(f"⚠️  SD VAE download failed: {e}\n")

# Download Whisper weights
print("⏳ Downloading Whisper...")
try:
    snapshot_download(
        repo_id="openai/whisper-tiny",
        local_dir=str(checkpoints_dir / "whisper"),
        allow_patterns=["config.json", "pytorch_model.bin", "preprocessor_config.json"]
    )
    print("✅ Whisper downloaded\n")
except Exception as e:
    print(f"⚠️  Whisper download failed: {e}\n")

# Download DWPose weights
print("⏳ Downloading DWPose...")
try:
    hf_hub_download(
        repo_id="yzd-v/DWPose",
        filename="dw-ll_ucoco_384.pth",
        local_dir=str(checkpoints_dir / "dwpose"),
        local_dir_use_symlinks=False
    )
    print("✅ DWPose downloaded\n")
except Exception as e:
    print(f"⚠️  DWPose download failed: {e}\n")

# Download SyncNet weights
print("⏳ Downloading SyncNet...")
try:
    hf_hub_download(
        repo_id="ByteDance/LatentSync",
        filename="latentsync_syncnet.pt",
        local_dir=str(checkpoints_dir / "syncnet"),
        local_dir_use_symlinks=False
    )
    print("✅ SyncNet downloaded\n")
except Exception as e:
    print(f"⚠️  SyncNet download failed: {e}\n")

# Download Face Parse Bisent weights (already done by gdown in the shell script)
print("⏳ Checking Face Parse Bisent weights...")
face_parse_file = checkpoints_dir / "face-parse-bisent" / "79999_iter.pth"
resnet_file = checkpoints_dir / "face-parse-bisent" / "resnet18-5c106cde.pth"

if face_parse_file.exists():
    print("✅ Face Parse Bisent weights already downloaded")
else:
    print("⚠️  Face Parse Bisent weights not found - should be downloaded by shell script")

if resnet_file.exists():
    print("✅ ResNet18 weights already downloaded")
else:
    print("⚠️  ResNet18 weights not found - should be downloaded by shell script")

print("\n🎉 Model download complete!")
print("\n📁 Models directory structure:")
print(f"   {checkpoints_dir}/")
for d in sorted(checkpoints_dir.glob("*/")):
    print(f"   ├── {d.name}/")
    for f in sorted(d.glob("*"))[:3]:  # Show first 3 files
        print(f"   │   ├── {f.name}")
    if len(list(d.glob("*"))) > 3:
        print(f"   │   └── ... ({len(list(d.glob('*')))-3} more files)")
