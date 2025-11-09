#!/usr/bin/env python3
"""
MuseTalk Requirements Sync Script

This script helps sync requirements files with uv project dependencies.
Run this after adding/removing dependencies with uv.
"""

import subprocess
import sys
from pathlib import Path

def run_command(cmd):
    """Run command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command '{cmd}': {e}")
        return None

def export_requirements():
    """Export current uv dependencies to requirements files"""
    
    print("🔄 Exporting uv dependencies to requirements files...")
    
    # Export to root requirements.txt
    print("📦 Updating requirements.txt...")
    result = run_command("uv export --format requirements-txt --output-file requirements.txt")
    if result is not None:
        print("✅ Updated requirements.txt")
    
    # Create API-specific requirements (subset for API deployment)
    api_deps = [
        "fastapi==0.104.1",
        "uvicorn[standard]==0.24.0", 
        "python-multipart==0.0.6",
        "aiohttp>=3.12.0",
        "aiofiles>=23.2.0",
        "pydantic>=2.5.0",
        "httpx>=0.25.2",
        "numpy==1.23.5",
        "torch==2.0.1",
        "torchvision==0.15.2",
        "torchaudio==2.0.2",
        "opencv-python==4.9.0.80",
        "librosa==0.11.0",
        "soundfile==0.12.1",
        "diffusers==0.30.2",
        "transformers==4.39.2",
        "accelerate==0.28.0",
        "huggingface_hub==0.30.2",
        "omegaconf",
        "tqdm>=4.66.1",
        "pillow>=10.1.0",
        "ffmpeg-python",
        "python-dotenv>=1.0.0",
    ]
    
    # Update API requirements
    api_req_path = Path("api/requirements.txt")
    api_req_path.parent.mkdir(exist_ok=True)
    
    with open(api_req_path, "w") as f:
        f.write("# 🚀 MuseTalk API Requirements (Generated from uv)\n")
        f.write("# Core dependencies needed for API deployment\n\n")
        for dep in api_deps:
            f.write(f"{dep}\n")
    
    print("✅ Updated api/requirements.txt")

def sync_from_uv():
    """Sync all dependencies from current uv lock"""
    print("🔄 Syncing dependencies from uv...")
    
    result = run_command("uv sync")
    if result is not None:
        print("✅ uv sync completed")
    else:
        print("❌ uv sync failed")
        return False
    
    return True

def install_from_requirements():
    """Install any missing dependencies from requirements files"""
    print("📦 Installing dependencies...")
    
    # Try to add dependencies that might be missing
    missing_deps = [
        "gdown",
        "requests", 
        "imageio[ffmpeg]",
        "moviepy",
    ]
    
    for dep in missing_deps:
        print(f"  Adding {dep}...")
        result = run_command(f"uv add {dep}")
    
    print("✅ Dependencies installation completed")

def main():
    """Main function"""
    print("🚀 MuseTalk Requirements Sync")
    print("=" * 50)
    
    # Check if we're in a uv project
    if not Path("pyproject.toml").exists():
        print("❌ No pyproject.toml found. Make sure you're in the project root.")
        sys.exit(1)
    
    # Sync from uv
    if not sync_from_uv():
        sys.exit(1)
    
    # Export to requirements files
    export_requirements()
    
    # Install any missing deps
    install_from_requirements()
    
    print("\n🎉 Requirements sync completed!")
    print("\nNext steps:")
    print("  • Use 'uv sync' to install all dependencies") 
    print("  • Use 'uv add package_name' to add new packages")
    print("  • Run this script again after adding packages to update requirements files")

if __name__ == "__main__":
    main()